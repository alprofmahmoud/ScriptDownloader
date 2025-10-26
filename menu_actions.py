#!/usr/bin/env python3

class MenuActions:
    def __init__(self, downloader, url_loader):
        self.downloader = downloader
        self.url_loader = url_loader

    def action_show_format(self):
        print("Show Format Fist and Download Option")
        self.downloader.show_format_list()
        return None

    def action_quick_download(self):
        print("Quick Download and Best Format Option")
        self.downloader.download_single_video()
        return None

    def action_download_thumbnails(self):
        print("Thumbnails Download Option")
        return None

    def action_playlist_download(self):
        print("Playlist download option")
        return None

    def action_show_formats_from_file(self):
        print("Show Formats List and Download Option")
        self.url_loader.show_formats_list_urls_from_file_and_download()

        return None

    def action_download_best_from_file(self):
        print("Download Best Format")
        self.url_loader.downloader_from_file_best_format()
        return None

    def action_download_with_format(self):
        print("Format Input Option")
        self.url_loader.downloader_from_file_with_select_format()
        return None

    # Navigation Actions
    def go_to_other_options(self):
        """Navigate to other options menu"""
        return "switch:other"

    def go_to_load_from_file(self):
        """Navigate to load from file menu"""
        return "switch:load_from_file"

    def go_to_back(self):
        """Go back to previous menu"""
        return "back"

    def exit_program(self):
        """Exit the application"""
        return "exit"
