from download_core import DownloadCore
from utils.status_manager import StatusManager
from query_manager import QueryManager
from display_query import DisplayQuery
from utils.validators import _is_valid_url_format
from config import PENDING_URLS_FILE


class LoadURLsFromFile:
    def __init__(self, urls_file=PENDING_URLS_FILE):
        self.urls_file = urls_file
        self.core = DownloadCore()
        self.status_obj = StatusManager()
        self.query_obj = QueryManager()
        self.display_obj = DisplayQuery()
        self.output_location = None
        self.required_video_quality = None
        self.query_instnce = None

    def read_url_from_file(self):
        urls = []
        try:
            with open(self.urls_file, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip()]
                remaining_urls = len(urls)
            if urls:
                first_url = urls[0]
                with open(self.urls_file, 'w', encoding='utf-8') as file:
                    file.writelines(line + "\n" for line in urls[1:])
                return first_url, remaining_urls
            else:
                return None, 0
        except FileNotFoundError:
            print(f"Not foud {self.urls_file}")
            return None, 0
        except Exception as e:
            print(f"Error: {e}")
            return None, 0

    def _validate_url(self, url):
        """Validate URL format before downloading"""
        if not url:
            return False
        if not _is_valid_url_format(url):
            print(f"❌ Invalid URL format: {url}")
            return False
        return True

    def show_formats_list_urls_from_file_and_download(self):
        # Show formats list urls from file
        # Options show formats list
        yt_opts_show_list = {
                'listformats': True,
                'quiet': True,
                'skip_download': True
                }
        # Options Download
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("❗No URLs found in file!")
            return False

        print(f"Total urls remaining: {total_urls}")
        while url is not None:
            if not self._validate_url(url):
                print(f"❗Skipping invalid URL: {url}")
                url, total_urls = self.read_url_from_file()
                continue
            # Show statusbar
            result = self.query_obj.query_by_url(url)
            if result is None:
                new_id = self.status_obj._generate_id()
                self.display_obj.show_not_found(new_id, total_urls)
            else:
                self.display_obj.show_from_file(result, total_urls)
            # Show formats list
            self.core.execute_core(url, yt_opts_show_list)
            # Download URL
            yt_opts = self.core._build_download_options()
            self.core.execute_core(url, yt_opts)
            url, total_urls = self.read_url_from_file()
            print(f"Total urls remaining: {total_urls}")

    def downloader_from_file_best_format(self):
        # Downlaod urls from file
        yt_opts = self.core.prepare_and_build_options(format_id='best')
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("❗No URLs found in file!")
            return False
        print(f"Total urls remaining: {total_urls}")
        while url is not None:
            if not self._validate_url(url):
                print(f"❗Skipping invalid URL: {url}")
                url, total_urls = self.read_url_from_file()
                continue
            # Show statusbar
            result = self.query_obj.query_by_url(url)
            if result is None:
                new_id = self.status_obj._generate_id()
                self.display_obj.show_not_found(new_id, total_urls)
            else:
                self.display_obj.show_from_file(result, total_urls)
            self.core.execute_core(url, yt_opts)
            url, total_urls = self.read_url_from_file()
            print(f"Total urls remaining: {total_urls}")

    def downloader_from_file_with_select_format(self):

        yt_opts = self.core._build_download_options()
        url, total_urls = self.read_url_from_file()
        if url is None:
            print("❗ No URLs found in file!")
            return False
        while url is not None:
            if not self._validate_url(url):
                print(f"❗Skipping invalid URL: {url}")
                url, total_urls = self.read_url_from_file()
                print(f"Total urls remaining: {total_urls}")
                continue
            # Show statusbar
            result = self.query_obj.query_by_url(url)
            if result is None:
                new_id = self.status_obj._generate_id()
                self.display_obj.show_not_found(new_id, total_urls)
            else:
                self.display_obj.show_from_file(result, total_urls)
            self.core.execute_core(url, yt_opts)
            url, total_urls = self.read_url_from_file()
