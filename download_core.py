import yt_dlp
import re
import os
import time
from datetime import datetime
from utils.status_manager import StatusManager
from utils.locations_manager import LocationsManager
from utils.formats_manager import FormatsManager
from config import HISTORY_FILE


class DownloadCore:
    def __init__(self, url=None):
        self.url = url
        self.status_manager = StatusManager(HISTORY_FILE)
        self.select_location = LocationsManager()
        self.select_format = FormatsManager()
        self.download_status = None
        self.percent_str = '0 %'
        self.stored_location = None
        self.format_id = None
        self.video_title = None
        self.video_id = None
        self.total_playlist_videos = None

    def _extract_info(self, d):
        """Extract common info from download dict"""
        percent_str_raw = d.get('_percent_str', '0%')
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str_raw).strip()
        info_dict = d.get('info_dict') or {}
        return {
            'percent_str': percent_str,
            'info_dict': info_dict,
            'playlist_title': info_dict.get('playlist_title'),
            'playlist_index': info_dict.get('playlist_index'),
            'playlist_count': info_dict.get('n_entries'),
            'format_id': info_dict.get('format_id', 'N/A'),
            'video_title': info_dict.get('title', 'N/A'),
            'video_id': info_dict.get('id')
        }

    def download_progress_hook(self, d):
        info = self._extract_info(d)
        self.percent_str = info['percent_str']
        info_dict = info['info_dict']
        playlist_title = info['playlist_title']
        playlist_index = info['playlist_index']
        playlist_count = info['playlist_count']
        video_id = info['video_id']
        # Progress hook for download updates
        if d['status'] == 'downloading':
            if self.download_status != 'downloading':
                self.download_status = 'downloading'
                self.video_title = info_dict.get('title', 'N/A')
                self.format_id = info_dict.get('format_id', 'N/A')
            if video_id:
                self.video_id = video_id

            # Update status
            if playlist_index is None:
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.stored_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title,
                    video_id=self.video_id
                    )

            else:
                video_url = info_dict.get('webpage_url') or \
                        info_dict.get('url')
                self.status_manager.update_status_by_url_playlist(
                    playlist_url=self.url,
                    video_url=video_url,
                    new_status=self.download_status,
                    stored_location=self.stored_location,
                    percent_str=self.percent_str,
                    format_id=self.format_id,
                    video_title=self.video_title,
                    video_id=self.video_id,
                    extra_info={
                            'playlist_title': playlist_title,
                            'playlist_index': playlist_index,
                            'playlist_count': playlist_count,
                            'total_playlist_videos': self.total_playlist_videos
                                }
                    )

        elif d['status'] == 'finished':
            print(" ✅ Download completed!")
            self.download_status = 'finished'
            self.format_id = info_dict.get('format_id', 'N/A')
            self.video_title = info_dict.get('title', 'N/A')
            if video_id:
                self.video_id = video_id
            if playlist_index is None:
                # Update status
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.stored_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title,
                    video_id=self.video_id
                    )
            else:
                video_url = info_dict.get('webpage_url') or \
                        info_dict.get('url')
                self.status_manager.update_status_by_url_playlist(
                    playlist_url=self.url,
                    video_url=video_url,
                    new_status=self.download_status,
                    stored_location=self.stored_location,
                    percent_str=self.percent_str,
                    format_id=self.format_id,
                    video_title=self.video_title,
                    video_id=self.video_id,
                    extra_info={
                            'playlist_title': playlist_title,
                            'playlist_index': playlist_index,
                            'playlist_count': playlist_count,
                            'total_playlist_videos': self.total_playlist_videos
                                }
                    )

    class _SilentLogger:
        """Suppresses yt-dlp's own console output during the pre-download
        probe. Without this, yt-dlp prints its own 'ERROR: ...' line to
        the console *and* our except block below prints a second, near-
        identical message for the same failure."""
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            pass

    def probe_video_info(self, url):
        """Extract full video metadata without downloading. Used for the
        pre-download duplicate check, filename collision resolution, and
        reused later by execute_core() to avoid extracting the same page
        twice. Returns None on failure (extractor error, unsupported URL,
        etc.) — callers must treat that as "continue without probing"."""
        probe_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'logger': self._SilentLogger(),
        }
        try:
            with yt_dlp.YoutubeDL(probe_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:  # noqa: BLE001
            # Keep this short: yt-dlp exception text for some extractors
            # (e.g. TikTok) includes a long "please report this issue..."
            # boilerplate that isn't useful here.
            short_reason = str(e).splitlines()[0].split('; please report')[0]
            print(f"Could not probe video info before download: {short_reason}")
            return None

    @staticmethod
    def _upload_date_to_epoch_seconds(upload_date):
        """Convert yt-dlp's upload_date ('YYYYMMDD') to epoch seconds.
        Falls back to the current time if the date is missing/invalid."""
        if upload_date:
            try:
                dt = datetime.strptime(upload_date, '%Y%m%d')
                return int(dt.timestamp())
            except ValueError:
                pass
        return int(time.time())

    def _resolve_outtmpl(self, video_info, stored_location):
        """Build the output template. If a file matching the default naming
        scheme already exists on disk (but the video was not found in
        history), disambiguate the filename using uploader + upload_date
        (as epoch seconds) instead of overwriting it."""
        base_dir = os.path.join(
            os.path.expanduser('~'), 'Downloads', stored_location
        )
        default_template = '%(title,uploader)s _ %(id)s.%(ext)s'

        if not video_info:
            return os.path.join(base_dir, default_template)

        title = video_info.get('title') or 'NA'
        video_id = video_info.get('id') or 'NA'
        ext = video_info.get('ext') or 'mp4'
        default_filename = f"{title} _ {video_id}.{ext}"
        default_path = os.path.join(base_dir, default_filename)

        if os.path.exists(default_path):
            uploader = video_info.get('uploader') or 'NA'
            epoch_seconds = self._upload_date_to_epoch_seconds(
                video_info.get('upload_date')
            )
            disambiguated_template = (
                f"%(title)s _ {uploader}_{epoch_seconds}.%(ext)s"
            )
            print(
                "A file with the same name already exists locally "
                "(not tracked in history) — renaming using uploader + "
                "upload timestamp to avoid overwriting it."
            )
            return os.path.join(base_dir, disambiguated_template)

        return os.path.join(base_dir, default_template)

    def execute_core(
            self,
            url,
            yt_opts=None,
            stored_location=None,
            format_id=None,
            location=None,
            preloaded_info=None
            ):
        # Execute download
        self.url = url
        if yt_opts is not None:
            if stored_location is not None:
                self.stored_location = stored_location
        else:
            yt_opts = self._build_download_options(
                    format_id=format_id,
                    location=location
                    )
        if not yt_opts:
            print("❌ Failed to build download options")
            return False
        try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                if preloaded_info is not None:
                    try:
                        # Reuse the info we already extracted during the
                        # pre-download probe instead of fetching/parsing
                        # the page again — this is what was making every
                        # download noticeably slower.
                        ydl.process_ie_result(preloaded_info, download=True)
                    except Exception:
                        # Cached info can go stale (e.g. expired CDN links
                        # on sites like TikTok/Instagram) if time passed
                        # between the probe and the actual download (menus,
                        # user input, etc). Fall back to a fresh extraction.
                        print("Cached video info could not be reused, re-fetching before download...")
                        ydl.download([url])
                else:
                    ydl.download([url])

        except KeyboardInterrupt:
            print("\n⏹️ Download cancelled by user!")
            self.download_status = 'cancelled'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.stored_location)
        except yt_dlp.utils.DownloadError as e:
            print(f"Download error: {e}")
            error_message = str(e)
            # Check error type
            if 'Private video' in error_message:
                print(f"❗Skipping private video  {error_message}")
                self.download_status = 'skipped_private'
            elif 'Video unavailable' in error_message:
                print(f"❗Skipping unavailable video {error_message}")
                self.download_status = 'skipped_unavailable'
            else:
                print(f"Download error: {e}")
                self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.stored_location)

        except yt_dlp.utils.ExtractorError as e:
            print(f"Extractor error: {e}")
            error_message = str(e)
            # Check error type
            if 'Private video' in error_message:
                print(f"❗Skipping private video  {error_message}")
                self.download_status = 'skipped_private'
            elif 'Video unavailable' in error_message:
                print(f"❗Skipping unavailable video {error_message}")
                self.download_status = 'skipped_unavailable'
            else:
                print(f"Extractor error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.stored_location)

        except Exception as e:
            print(f"Unexpected error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.stored_location)

    def _build_download_options(self,
                                format_override=None,
                                format_id=None,
                                location=None,
                                video_info=None
                                ):
        format_value = format_id if format_id is not None else \
                format_override if format_override else self.select_format.select_format()
        # Translate the selected quality preset (e.g. '720p') into an
        # actual yt-dlp format selector + optional format_sort rule.
        # Works the same for a raw/custom format string too (passed
        # straight through), so resuming an old download from history
        # still behaves exactly as before.
        format_selector, format_sort = FormatsManager.resolve(format_value)
        # Select output location
        self.stored_location = location if location is not None else \
            self.select_location.select_location()
        if self.stored_location is None:  # If user canceled selection
            print("❌ No location selected!")
            return False

        options = {
            'format': format_selector,
            'outtmpl': self._resolve_outtmpl(video_info, self.stored_location),
            'merge_output_format': 'mp4',
            'no_warnings': True,
            'ignoreerrors': True,
            # 'quiet': True,
            'progress_hooks': [self.download_progress_hook],

            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # Truncate title to 150 characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'^(.{1,150}).*$', '\\1'),
                    # Remove quotes from title
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'["\']', ''),
                    # Remove hashtags, numbers with K, and specific words
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title',
                     r'#\S*|\d+\.?\d*K|'
                     r'\b(views|reactions|subscribers|4k)\b', ''),
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'[|｜❙•·\-–—]', ''),
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'\s+', ' '),
                    # Remove leading and trailing spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'^\s+|\s+$', ''),
                ],
                'when': 'pre_process'
            }]
            }

        if format_sort:
            options['format_sort'] = format_sort

        return options

    def prepare_and_build_options(self, format_id=None):
        return self._build_download_options(format_override=format_id)
