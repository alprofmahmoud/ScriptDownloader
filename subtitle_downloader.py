import os
import yt_dlp
from utils.validators import _is_valid_url_format, get_valid_url
from utils.locations_manager import LocationsManager


class SubtitleDownloader:
    def __init__(self):
        self.select_location = LocationsManager()

    def _list_subtitles(self, url):
        """Fetch available subtitles without downloading the video.
        Returns (manual_subs, auto_subs) as yt-dlp's own dicts
        (lang_code -> list of format entries), or (None, None) on failure."""
        opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:  # noqa: BLE001
            print(f"Could not fetch subtitle list: {e}")
            return None, None
        return info.get('subtitles') or {}, info.get('automatic_captions') or {}

    def download_subtitles(self, url=None):
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False

        manual_subs, auto_subs = self._list_subtitles(url)
        if manual_subs is None:
            return False

        # Manual (human-made) subtitles are listed first since they're
        # usually higher quality than auto-generated captions.
        entries = [(lang, False) for lang in manual_subs]
        entries += [(lang, True) for lang in auto_subs if lang not in manual_subs]

        if not entries:
            print("No subtitles available for this video.")
            return False

        print("Available subtitles:")
        for i, (lang, is_auto) in enumerate(entries, 1):
            tag = "auto-generated" if is_auto else "manual"
            print(f"  {i}) {lang} ({tag})")

        choice = input("Select subtitle number: ").strip()
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(entries):
                raise ValueError
        except ValueError:
            print("❌ Invalid selection.")
            return False

        lang, is_auto = entries[idx]

        location = self.select_location.select_location()
        if location is None:
            print("❌ No location selected!")
            return False

        yt_opts = {
            'skip_download': False,
            'writesubtitles': not is_auto,
            'writeautomaticsubtitles': is_auto,
            'subtitleslangs': [lang],
            # 'best' lets yt-dlp pick the best subtitle format the site
            # actually offers (srt/vtt/ttml/etc.) for that language.
            'subtitlesformat': 'best',
            'outtmpl': os.path.join(location, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download([url])
            print(f"Subtitle downloaded: {lang} ({'auto-generated' if is_auto else 'manual'})")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"Could not download subtitle: {e}")
            return False
