"""
utils/status_manager.py — نسخة مبنية على Supabase

نفس الكلاسات والدوال والتوقيعات القديمة بالظبط (HistoryReader, StatusManager,
update_status_by_url, update_status_by_url_playlist, _calculate_playlist_status,
_read_history, _write_history) — عشان باقي الملفات (query_manager.py,
download_core.py, single_downloader.py, playlist_download.py,
load_urls_from_file.py) تشتغل من غير أي تعديل فيها إلا سطر واحد في
query_manager.py (موضّح في SUPABASE_SETUP.md).

الفكرة:
- الملف المحلي (data/download_history.json) لسه بيتكتب دايمًا كنسخة احتياطية
  سريعة وضمان إن الأداة تشتغل حتى من غير نت.
- Supabase هو مصدر الحقيقة المشترك بين الأجهزة: القراءة بتحاول منه الأول.
- عشان مانحمّلش الشبكة بمئات الطلبات وقت التحميل (progress hook بيتنادى
  كذا مرة في الثانية)، تحديثات حالة "downloading" بس بتتبعت لـ Supabase
  بحد أقصى مرة كل PROGRESS_THROTTLE_SECONDS. أي حالة نهائية
  (finished/error/cancelled/skipped_*) بتتبعت فورًا من غير تأخير.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests

from config import HISTORY_FILE
from filelock import FileLock

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TABLE_NAME = "download_history"
# Kept short on purpose: this request runs synchronously inside the
# download progress hook, so a long timeout here is what made Ctrl+C feel
# "stuck" if pressed while a push to Supabase was in flight on a slow
# connection — Python can't interrupt a blocking network call mid-flight.
REQUEST_TIMEOUT = 4  # seconds

PROGRESS_THROTTLE_SECONDS = 1.5

_supabase_checked = False
_supabase_ok = False
_last_sync_time: Dict[str, float] = {}


def _supabase_ready() -> bool:
    """Checks Supabase credentials once per run."""
    global _supabase_checked, _supabase_ok
    if _supabase_checked:
        return _supabase_ok
    _supabase_checked = True
    if not SUPABASE_URL or not SUPABASE_KEY:
        env_path = Path(__file__).resolve().parent.parent / '.env'
        print(
            f"SUPABASE_URL / SUPABASE_KEY not found (looked in {env_path}) — "
            "falling back to the local file only (no cloud sync)."
        )
        _supabase_ok = False
    else:
        _supabase_ok = True
    return _supabase_ok


def _headers(prefer: str = "") -> Dict[str, str]:
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _rest_url(query: str = "") -> str:
    return f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}{query}"


def _supabase_select_all() -> Optional[List[Dict[str, Any]]]:
    """GET كل الصفوف. بيرجع None لو فشل الاتصال (عشان نفرّق عن 'فاضي فعلاً')."""
    if not _supabase_ready():
        return None
    try:
        resp = requests.get(
            _rest_url("?select=id,payload&order=id.asc"),
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:  # noqa: BLE001
        print(f"Could not read history from Supabase ({e}) — using the local copy.")
        return None


def _supabase_upsert(entry_id, payload: Dict[str, Any]) -> None:
    if not _supabase_ready():
        return
    try:
        resp = requests.post(
            _rest_url("?on_conflict=id"),
            headers=_headers(prefer="resolution=merge-duplicates"),
            json={"id": entry_id, "payload": payload},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"Could not push update to Supabase ({e}) — saved locally, will sync automatically on next run.")


def _supabase_delete(entry_id) -> None:
    if not _supabase_ready():
        return
    try:
        resp = requests.delete(
            _rest_url(f"?id=eq.{entry_id}"),
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"Deleted locally, but could not delete from Supabase ({e}).")


class HistoryReader:
    def __init__(self, history_file=HISTORY_FILE):
        self.history_file = history_file

    # ---- محلي ----
    def _read_local(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _write_local(self, data) -> bool:
        lock = FileLock(self.history_file + ".lock")
        try:
            with lock:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False

    # ---- القراءة العامة (كانت اسمها _read_history في الأصلي) ----
    def _read_history(self) -> List[Dict[str, Any]]:
        rows = _supabase_select_all()
        if rows is None:
            # فشل الاتصال بـ Supabase (مفيش نت / مفاتيح غلط) — رجّع النسخة المحلية
            return self._read_local()
        if not rows:
            # الجدول لسه فاضي (أول مرة) — استخدم النسخة المحلية لو موجودة
            return self._read_local()
        return [row["payload"] for row in rows]

    # ---- الكتابة العامة (نفس الاسم القديم _write_history) ----
    # بتكتب النسخة المحلية دايمًا (نفس سلوك الكود الأصلي بالظبط).
    # المزامنة مع Supabase بتتم بشكل منفصل في StatusManager._push_entry
    # (عشان الكتابة المتكررة أثناء التحميل متبقاش بطيئة).
    def _write_history(self, data) -> bool:
        return self._write_local(data)

    # ---- حذف سطر بعينه من Supabase (مستخدم في query_manager.delete_by_id) ----
    def _sync_delete(self, entry_id) -> None:
        _supabase_delete(entry_id)

    # ---- Automatic two-way sync, run once at startup (see main_sd.py) ----
    def sync_with_cloud(self) -> bool:
        """Best-effort two-way sync between the local file and Supabase.

        1. Pull all rows from Supabase and merge them into the local file
           (cloud entries win on id conflicts, since Supabase is the shared
           source of truth across devices).
        2. Push any local-only entries that are missing from the cloud
           (e.g. entries saved earlier while a push had failed, such as
           during an auth/permission error).

        Returns True if a pull actually happened (i.e. we're online and
        configured), False otherwise — callers can use this to decide
        whether the local file is already up to date with the cloud.
        """
        cloud_rows = _supabase_select_all()
        if cloud_rows is None:
            return False

        local_data = self._read_local()
        local_by_id = {entry.get('id'): entry for entry in local_data}
        cloud_by_id = {row.get('id'): row.get('payload', {}) for row in cloud_rows}

        merged = dict(local_by_id)
        merged.update(cloud_by_id)
        self._write_local(list(merged.values()))

        # Retry pushing anything that only exists locally so far
        for entry_id, entry in local_by_id.items():
            if entry_id not in cloud_by_id:
                _supabase_upsert(entry_id, entry)

        return True

    # ---- lookup by video_id, used for the pre-download duplicate check ----
    # Reads the local file only: sync_with_cloud() is expected to run once
    # at startup, so by the time downloads start the local file already
    # mirrors the cloud. This keeps the per-download check fast and free
    # of network dependency.
    def find_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Search both single-video entries and nested playlist videos
        for a matching video_id. Returns a small summary dict or None."""
        if not video_id:
            return None
        all_downloads = self._read_local()

        # Regular (non-playlist) entries
        for entry in all_downloads:
            if entry.get('video_id') == video_id:
                return {
                    'id': entry.get('id'),
                    'location': entry.get('location'),
                    'status': entry.get('status'),
                    'is_playlist_video': False,
                }

        # Videos nested inside a playlist entry
        for entry in all_downloads:
            for video in entry.get('videos', []):
                if video.get('video_id') == video_id:
                    return {
                        'id': entry.get('id'),
                        'playlist_title': entry.get('playlist_title'),
                        'location': video.get('location'),
                        'status': video.get('status'),
                        'is_playlist_video': True,
                    }
        return None


class StatusManager(HistoryReader):
    def _generate_id(self) -> int:
        all_downloads = self._read_history()
        if not all_downloads:
            return 1
        max_id = max(entry.get('id', 0) for entry in all_downloads)
        return max_id + 1

    def _push_entry(self, entry: Dict[str, Any], key: str, force: bool = False) -> None:
        """يرفع سطر واحد بس لـ Supabase (upsert)، مع throttling لتحديثات
        'downloading' المتكررة. الحالات النهائية بتتبعت فورًا (force)."""
        status = entry.get('status')
        if not force and status == 'downloading':
            now = time.monotonic()
            last = _last_sync_time.get(key, 0.0)
            if now - last < PROGRESS_THROTTLE_SECONDS:
                return
            _last_sync_time[key] = now
        else:
            _last_sync_time[key] = time.monotonic()
        _supabase_upsert(entry.get('id'), entry)

    def update_status_by_url(self, url, new_status,
                             stored_location=None,
                             percent_str='0%',
                             format_id=None,
                             video_title=None,
                             extra_info=None,
                             video_id=None):
        # Update status for existing URL or add new entry if not found
        if not url:
            return
        # Local-only read: see the comment on the playlist variant below
        # for why this must not go through _read_history() (Supabase) on
        # every progress-hook tick.
        all_downloads = self._read_local()

        found = False
        target_entry = None
        for entry in all_downloads:
            if entry.get('url') == url:
                entry['status'] = new_status
                if stored_location is not None:
                    entry['location'] = stored_location
                entry['percent_str'] = percent_str
                found = True
                entry['format_id'] = format_id
                entry['video_title'] = video_title
                if video_id is not None:
                    entry['video_id'] = video_id
                target_entry = entry
                break
        if not found:
            target_entry = {
                'id': self._generate_id(),
                'url': url,
                'video_id': video_id,
                'status': new_status,
                'location': stored_location,
                'percent_str': percent_str,
                'format_id': format_id,
                'video_title': video_title
            }
            all_downloads.append(target_entry)

        result = self._write_history(all_downloads)
        self._push_entry(target_entry, key=url, force=(not found) or new_status != 'downloading')
        return result

    def update_status_by_url_playlist(self,
                                      playlist_url,
                                      video_url,
                                      new_status,
                                      stored_location=None,
                                      percent_str='0%',
                                      format_id=None,
                                      video_title=None,
                                      extra_info=None,
                                      video_id=None,
                                      ):
        if not playlist_url or not video_url:
            return
        # Local-only read: this fires on every progress-hook tick during a
        # download (many times per second). Reading via _read_history()
        # here meant a full Supabase GET request on every single tick,
        # which was the main cause of the tool feeling slow. The local
        # file is already kept in sync with the cloud by sync_with_cloud()
        # at startup and by the (throttled) pushes in _push_entry.
        all_downloads = self._read_local()
        extra_info = extra_info or {}
        playlist_title = extra_info.get('playlist_title')
        total_videos = extra_info.get('total_playlist_videos')
        playlist_index = extra_info.get('playlist_index')
        playlist_count = extra_info.get('playlist_count')
        percent_playlist = extra_info.get('percent_playlist')

        playlist_found = False
        target_entry = None
        for entry in all_downloads:
            if entry.get('playlist_url') == playlist_url:
                playlist_found = True
                if playlist_title:
                    entry['playlist_title'] = playlist_title
                if total_videos:
                    entry['total_videos'] = total_videos
                if playlist_count:
                    entry['playlist_count'] = playlist_count
                if 'videos' not in entry:
                    entry['videos'] = []
                video_found = False
                for video in entry['videos']:
                    if video.get('url') == video_url:
                        video['status'] = new_status
                        video['percent_str'] = percent_str
                        video['video_title'] = video_title
                        video['format_id'] = format_id
                        if stored_location:
                            video['location'] = stored_location
                        if playlist_index is not None:
                            video['playlist_index'] = playlist_index
                        if video_id is not None:
                            video['video_id'] = video_id
                        video_found = True
                        break
                if not video_found:
                    entry['videos'].append({
                        'url': video_url,
                        'video_id': video_id,
                        'video_title': video_title,
                        'status': new_status,
                        'percent_str': percent_str,
                        'format_id': format_id,
                        'location': stored_location,
                        'playlist_index': playlist_index
                    })
                entry['status'] = self._calculate_playlist_status(entry['videos'])
                target_entry = entry
                break
        if not playlist_found:
            target_entry = {
                'id': self._generate_id(),
                'playlist_url': playlist_url,
                'playlist_title': playlist_title,
                'total_videos': total_videos,
                'playlist_count': playlist_count,
                'percent_playlist': percent_playlist,
                'status': new_status,
                'videos': [{
                    'url': video_url,
                    'video_id': video_id,
                    'video_title': video_title,
                    'status': new_status,
                    'percent_str': percent_str,
                    'format_id': format_id,
                    'location': stored_location,
                    'playlist_index': playlist_index
                }]
            }
            all_downloads.append(target_entry)

        result = self._write_history(all_downloads)
        overall_status = target_entry.get('status')
        self._push_entry(
            target_entry,
            key=playlist_url,
            force=(not playlist_found) or overall_status != 'downloading'
        )
        return result

    def _calculate_playlist_status(self, videos):
        """Calculate overall playlist status based on videos.

        ملحوظة: الكود الأصلي كان بيدوّر على status == 'failed'، لكن
        download_core.py بيسجل الحالة فعليًا كـ 'error' — فالباج ده
        كان بيخلي البلاي‌ليست الفاشلة ترجع 'queued' غلط بدل 'failed'.
        هنا اتوحدت القيمة لـ 'error' زي ما فعليًا بيتسجل في كل مكان.
        """
        if not videos:
            return 'queued'
        statuses = [v.get('status') for v in videos]
        if all(s == 'finished' for s in statuses):
            return 'finished'
        if any(s == 'downloading' for s in statuses):
            return 'downloading'
        if any(s == 'error' for s in statuses):
            return 'error'
        return 'queued'
