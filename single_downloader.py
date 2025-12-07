from typing import Optional
import copy
from utils.validators import _is_valid_url_format, get_valid_url
from download_core import DownloadCore
from utils.status_manager import StatusManager
from query_manager import QueryManager
from display_query import DisplayQuery


class SingleDownloader:
    def __init__(self, url=None):
        self.url = url
        self.core = DownloadCore()
        self.query_obj = StatusManager()
        self.query_object = QueryManager()
        self.display_obj = DisplayQuery()

    def show_format_list(self, url: Optional[str] = None):
        # Show available formats for a video
        # Get URL from any source
        url = url or get_valid_url(allow_quit=True)
        if url is None:  # User chose exit
            return
        # Validate URL
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return
        # Update self.url
        self.url = None
        yt_opts = {
            'listformats': True,
            'skip_download': True
            }
        self.core.execute_core(url, yt_opts)
        return True

    def download_single_video(
            self,
            url: Optional[str] = None,
            required_video_quality: Optional[str] = None,
            custom_options: Optional[dict] = None
            ):
        # Get input if not provided
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False
        self.url = None
        # Show statusbar
        result = self.query_object.query_by_url(url)
        if result is None:
            new_id = self.query_obj._generate_id()
            self.display_obj.show_not_found(new_id)
        else:
            self.display_obj.show_single(result)

        """
        # else:
            # self.required_video_quality =
             'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best'
            # self.required_video_quality =
            'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best'
            #self.required_video_quality = '298+140'
            #self.required_video_quality = 'sd'
        """
        # Setup download options
        # Build base options always
        options = self.core._build_download_options()

        if not options:
            return False

        # ✅ If custom_options exist, merge them with base options
        # Merge custom options
        if custom_options:
            custom_copy = copy.deepcopy(custom_options)
            if 'postprocessors' in custom_copy:
                custom_processors = custom_copy.pop('postprocessors')
                existing_processors = options.get('postprocessors', [])
                options['postprocessors'] = existing_processors + custom_processors
            options.update(custom_copy)
        # Execute download
        self.core.execute_core(url, options)
        return True

    def download_single_by_id(self, url, format_id, location):
        """ Download by id from history file """
        # Return download options
        return self.core.execute_core(
                url=url,
                format_id=format_id,
                location=location
                )

    def download_by_user_agent(
            self,
            url: Optional[str] = None,
            http_headers: Optional[dict] = None
            ):
        # Default user agent if not provided
        if http_headers is None:
            http_headers = {
                    'User-Agent': (
                        'Mozilla/5.0 (Linux; Android 13) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/120.0.6099.43 Mobile Safari/537.36'
                        ),
                    'Accept': (
                        'text/html,application/xhtml+xml,'
                        'application/xml;q=0.9,*/*;q=0.8'
                        ),
                    'Accept-Language': 'en-US,en;q=0.9'
                    }
            # Prepare custom options
        custom_options = {
                    'http_headers': http_headers
                }
        return self.download_single_video(
                url=url,
                custom_options=custom_options
                )

    def download_and_embed_thumbnails(self, url=None):
        # self.show_format_list()
        custom_options = {
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
                {'key': 'EmbedThumbnail'},
            ]
        }
        return self.download_single_video(
                url=url,
                custom_options=custom_options
                )
