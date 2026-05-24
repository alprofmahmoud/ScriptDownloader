import yt_dlp
import re
import os
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
            'video_title': info_dict.get('title', 'N/A')
        }

    def download_progress_hook(self, d):
        info = self._extract_info(d)
        self.percent_str = info['percent_str']
        info_dict = info['info_dict']
        playlist_title = info['playlist_title']
        playlist_index = info['playlist_index']
        playlist_count = info['playlist_count']
        # Progress hook for download updates
        if d['status'] == 'downloading':
            if self.download_status != 'downloading':
                self.download_status = 'downloading'
                self.video_title = info_dict.get('title', 'N/A')
                self.format_id = info_dict.get('format_id', 'N/A')

            # Update status
            if playlist_index is None:
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.stored_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title
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
            if playlist_index is None:
                # Update status
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.stored_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title
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
                    extra_info={
                            'playlist_title': playlist_title,
                            'playlist_index': playlist_index,
                            'playlist_count': playlist_count,
                            'total_playlist_videos': self.total_playlist_videos
                                }
                    )

    def execute_core(
            self,
            url,
            yt_opts=None,
            stored_location=None,
            format_id=None,
            location=None
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
                                location=None
                                ):
        format_value = format_id if format_id is not None else \
                format_override if format_override else self.select_format.select_format()
        # Select output location
        self.stored_location = location if location is not None else \
            self.select_location.select_location()
        if self.stored_location is None:  # If user canceled selection
            print("❌ No location selected!")
            return False

        return {
            'format': format_value,
            'outtmpl': os.path.join(os.path.expanduser('~'), self.stored_location, '%(title)s.%(ext)s'),
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

    def prepare_and_build_options(self, format_id=None):
        return self._build_download_options(format_override=format_id)
