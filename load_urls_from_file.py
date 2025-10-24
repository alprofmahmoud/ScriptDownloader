#!/user/bin/env python3

import yt_dlp
from single_downloader_mode_sd import SingleDownloader
from utils.select_output_location import select_output_location

class LoadURLsFromFile:
    def __init__(self, file_urls="./urls.txt"):
        self.file_urls = file_urls
        self.execute_download_urls_from_file = SingleDownloader()
        self.output_location = None
    

    def read_url_from_file(self):
        urls = []
        try:
            with open(self.file_urls, 'r', encoding='utf-8') as file:
                for line_file in file:
                    urls.append(line_file.strip())
                return urls
        except FileNotFoundError:
            print(f"Not foud {self.file_urls}")
        except Exception as e:
            print(f"Error: {e}")

    def downloader_from_file(self):
        # Downlaod urls from file

        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # User not selected location
            print("❌ No location selected!")
            return False

        # Download options 
        yt_opts = {
            'outtmpl': f'$HOME/{self.output_location}/reels/%(title).100s.%(ext)s',
            'format': 'best',
            'merge_output_format': 'mp4',
            'progress_hooks': [self.execute_download_urls_from_file.download_progress_hook],
            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'[|｜❙•\-–—]', ''),
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'\s+', ' ')
                ],
                'when': 'pre_process'
            }]
            }

        urls = self.read_url_from_file()
        for url in urls:
            self.execute_download_urls_from_file.execute_download(url, yt_opts, self.output_location)

    def show_formats_list_urls_from_file(self):
        # Show formats list urls from file

        # Download options
        yt_opts_from_url = {
            'outtmpl': f'$HOME/{self.output_location}/reels/%(title).100s.%(ext)s',
            'format': 'best',
            'merge_output_format': 'mp4',
            'progress_hooks': [self.execute_download_urls_from_file.download_progress_hook],
            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'[|｜❙•\-–—]', ''),
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'\s+', ' ')
                ],
                'when': 'pre_process'
            }]
            }

        yt_opts = {
                'listformats': True,
                'skip_download': True
                }

        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # User not selected location
            print("❌ No location selected!")
            return False

        urls = self.read_url_from_file()
        for url in urls:
            # Show formats list
            self.execute_download_urls_from_file.execute_download(url, yt_opts)
            # Download URLs
            self.execute_download_urls_from_file.execute_download(url, yt_opts_from_url, self.output_location)
       
# Test functions calls
#urls = LoadURLsFromFile()
#urls.show_format_list_urls_from_file()
#urls.downloader_from_file()
