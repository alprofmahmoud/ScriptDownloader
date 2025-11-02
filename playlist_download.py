#!/usr/bin/env python3
import yt_dlp
from single_downloader_mode_sd import SingleDownloader
from utils.validators import _is_valid_url_format, get_valid_url
from utils.select_output_location import select_output_location


class PlaylistOption:
    def __init__(self, url=None):
        self.url = url
        self.execute_playlist_download = SingleDownloader()
        self.output_location = None

    def playlist_download(self, url=None):
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False
        self.url = None

        # Extract total videos
        with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            total_videos = len(info.get('entries', []))
            # Pass total videos to SingleDownloader class
            self.execute_playlist_download.total_playlist_videos = total_videos

        print("Start playlist video number:")
        start_item = input()
        print("End playlist video number:")
        end_item = input()

        # Select output location
        self.execute_playlist_download.output_location \
            = select_output_location()
        if self.execute_playlist_download.output_location is None:
            print("❌ No location selected!")
            return False

        yt_opts = {
            'playliststart': start_item,
            'playlistend': end_item,
            'outtmpl': (
                f'$HOME/{self.execute_playlist_download.output_location}'
                f'/%(playlist_title)s/%(title).100s.%(ext)s'
                ),
            'format': 'best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'embed_metadata': True,
            'progress_hooks': [self.execute_playlist_download
                               .download_progress_hook],
            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'[|｜❙•\-–—]', ''),
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'\s+', ' ')
                ],
                'when': 'pre_process'
            }]
            }
        self.execute_playlist_download.execute_download(url, yt_opts)
