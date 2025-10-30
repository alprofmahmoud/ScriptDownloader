#!/user/bin/env python3

import yt_dlp
from single_downloader_mode_sd import SingleDownloader
from utils.select_output_location import select_output_location
from utils.select_format import select_format
from utils.status_manager import StatusManager
from query_url import display_query_url


class LoadURLsFromFile:
    def __init__(self, file_urls="./urls.txt"):
        self.file_urls = file_urls
        self.execute_download_urls_from_file = SingleDownloader()
        self.query_obj = StatusManager()
        self.output_location = None
        self.required_video_quality = None
        self.query_instnce = None

    def read_url_from_file(self):
        urls = []
        try:
            with open(self.file_urls, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip()]
                remaining_urls = len(urls)
            if urls:
                first_url = urls[0]
                with open(self.file_urls, 'w', encoding='utf-8') as file:
                    file.writelines(line + "\n" for line in urls[1:])
                return first_url, remaining_urls
            else:
                return None, 0
        except FileNotFoundError:
            print(f"Not foud {self.file_urls}")
            return None, 0
        except Exception as e:
            print(f"Error: {e}")
            return None, 0

    def _build_download_options(self, format_id):
        return {
            'outtmpl': f'$HOME/{self.output_location}/%(title).100s.%(ext)s',
            'format': format_id,
            'merge_output_format': 'mp4',
            'quiet': True,
            'progress_hooks': [
                self.execute_download_urls_from_file.download_progress_hook],
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

    def show_formats_list_urls_from_file_and_download(self):
        # Show formats list urls from file

        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # User not selected location
            print("❌ No location selected!")
            return False
        # Options show formats list
        yt_opts = {
                'listformats': True,
                'quiet': True,
                'skip_download': True
                }
        # Options Download
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("⚠️ No URLs found in file!")
            return False

        print(f"Total urls remaining: {total_urls}")
        while url is not None:
            # Show formats list
            self.execute_download_urls_from_file.execute_download(url, yt_opts)
            self.required_video_quality = select_format()
            # Download URLL
            yt_opts = self._build_download_options(self.required_video_quality)
            self.execute_download_urls_from_file.execute_download(
                    url,
                    yt_opts
                    )
            url, total_urls = self.read_url_from_file()
            print(f"Total urls remaining: {total_urls}")

    def downloader_from_file_best_format(self):
        # Downlaod urls from file
        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # User not selected location
            print("❌ No location selected!")
            return False
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("⚠️ No URLs found in file!")
            return False
        print(f"Total urls remaining: {total_urls}")
        while url is not None:
            query_url = self.query_obj.query_by_url(url)
            self.query_instance = display_query_url(query_url, total_urls)
            yt_opts = self._build_download_options('best')
            self.execute_download_urls_from_file.execute_download(url, yt_opts)
            url, total_urls = self.read_url_from_file()
            print(f"Total urls remaining: {total_urls}")

    def downloader_from_file_with_select_format(self):
        # Downlaod urls from file with select format

        self.required_video_quality = select_format()
        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # User not selected location
            print("❌ No location selected!")
            return False
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("⚠️ No URLs found in file!")
            return False
        print(f"Total urls remaining: {total_urls}")
        while url is not None:
            yt_opts = self._build_download_options(self.required_video_quality)
            self.execute_download_urls_from_file.execute_download(url, yt_opts)
            url, total_urls = self.read_url_from_file()
            print(f"Total urls remaining: {total_urls}")
