import yt_dlp
from download_core import DownloadCore
from utils.validators import _is_valid_url_format, get_valid_url
from query_manager import QueryManager
from utils.status_manager import StatusManager
from display_query import DisplayQuery


class PlaylistOption:
    def __init__(self, url=None):
        self.url = url
        self.execute_playlist = DownloadCore()
        self.query_obj = QueryManager()
        self.status_obj = StatusManager()
        self.display_obj = DisplayQuery()
        self.output_location = None

    def playlist_download(self, url=None):
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False
        self.url = None

        # Show statusbar
        result = self.query_obj.query_by_url(url)
        if result is None:
            new_id = self.status_obj._generate_id()
            self.display_obj.show_not_found(new_id)
        else:
            self.display_obj.show_playlist(result)
        # Extract total videos
        with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            total_videos = len(info.get('entries', []))
            # Pass total videos to SingleDownloader class
            self.execute_playlist.total_playlist_videos = total_videos
        try:
            start_item = int(input("Start playlist video number: "))
            end_item = int(input("End playlist video number: "))
            if start_item < 1:
                print("❌ Start number must be 1 or greater")
                return False
            if end_item < start_item:
                print("❌ End number must be greater than or equal to start number")
                return False
        except ValueError:
            print("❌ Please enter valid numbers")
            return False
        options = self.execute_playlist._build_download_options()
        options['playliststart'] = start_item
        options['playlistend'] = end_item
        options['outtmpl'] = (options['outtmpl'].replace(
            '/%(title)s.%(ext)s',
            '/%(playlist_title)s/%(title)s.%(ext)s'
            ))
        self.execute_playlist.execute_core(url, options)
