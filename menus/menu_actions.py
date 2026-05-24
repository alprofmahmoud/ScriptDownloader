from utils.formats_manager import FormatsManager


class MenuActions:
    def __init__(
            self,
            downloader,
            query_by,
            display_query,
            url_loader,
            playlist_download
            ):
        self.downloader = downloader
        self.query_by = query_by
        self.display_query = display_query
        self.url_loader = url_loader
        self.playlist_download = playlist_download
        self.format_obj = FormatsManager()

    def action_show_format(self):
        print("Show Format First Option")
        self.downloader.show_format_list()
        return None

    def action_quick_download(self):
        print("Quick Download and Best Format Option")
        self.downloader.download_single_video()
        return None

    def action_download_thumbnails(self):
        print("Thumbnails Download Option")
        self.downloader.download_and_embed_thumbnails()
        return None

    def action_query_by_id(self):
        print("Query by ID")
        result = self.query_by.query_by_id()
        if result:
            url, format_id, location = result
            self.downloader.download_single_by_id(url, format_id, location)
        return None

    def action_query_all_incompeleted(self):
        print("All incompleted")
        result = self.query_by.query_by_status(
                statuses=["error", "downloading"]
                )
        self.display_query.show_downloads_table(result)
        return None

    def action_delete_by_id(self):
        print("Delete by ID")
        self.query_by.delete_by_id()
        return None

    def action_query_by_status(self):
        result = self.query_by.query_by_status("downloading")
        self.display_query.show_downloads_table(result)
        return "switch:query"

    def action_playlist_download(self):
        print("Playlist download option")
        self.playlist_download.playlist_download()
        return None

    def action_download_by_user_agent(self):
        print("Download by User Agent")
        self.downloader.download_by_user_agent()
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
