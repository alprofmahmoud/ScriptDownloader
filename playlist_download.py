import os
import re
import yt_dlp
from download_core import DownloadCore
from utils.validators import _is_valid_url_format, get_valid_url
from query_manager import QueryManager
from utils.status_manager import StatusManager
from display_query import DisplayQuery


def _sanitize_for_filesystem(name):
    """Strip characters that are invalid in folder/file names on most
    filesystems (Jellyfin folder names must be filesystem-safe)."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()


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

        # Fetch the playlist's live info (title + total video count)
        # BEFORE showing the status line. Previously this ran *after*, so
        # if a saved history entry for this URL was missing some fields
        # (e.g. from an earlier interrupted attempt), the status line
        # always printed "N/A" instead of the real, currently-available
        # numbers.
        try:
            with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            total_videos = len(info.get('entries', []))
            live_playlist_title = info.get('title')
        except Exception as e:  # noqa: BLE001
            print(f"Could not fetch playlist info: {e}")
            total_videos = None
            live_playlist_title = None
        self.execute_playlist.total_playlist_videos = total_videos

        # Show statusbar using the fresh numbers above, plus any saved
        # location/progress from a previous attempt at this same playlist.
        result = self.query_obj.query_by_url(url)
        if result is None:
            new_id = self.status_obj._generate_id()
            self.display_obj.show_not_found(new_id)
        else:
            if total_videos is not None:
                result['total_videos'] = total_videos
            if live_playlist_title:
                result['playlist_title'] = live_playlist_title
            self.display_obj.show_playlist(result)
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

    def download_series_jellyfin(self, url=None):
        """Download a playlist as a TV series using Jellyfin's expected
        folder/file naming convention:
            Series Name (Year)/Season 01/Series Name (Year) S01E03 - Title.ext
        """
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False

        # Year is asked AFTER the URL, as requested.
        year_input = input("Series year (e.g. 2021): ").strip()
        if not re.fullmatch(r'\d{4}', year_input):
            print("❌ Please enter a valid 4-digit year.")
            return False
        year = year_input

        season_input = input("Season number (e.g. 1): ").strip()
        try:
            season = int(season_input)
            if season < 1:
                raise ValueError
        except ValueError:
            print("❌ Please enter a valid season number (1 or greater).")
            return False

        # Fetch the playlist's live info (title + total video count) to
        # use as the series name and to show real numbers, same approach
        # as the regular playlist_download().
        try:
            with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            total_videos = len(info.get('entries', []))
            live_playlist_title = info.get('title')
        except Exception as e:  # noqa: BLE001
            print(f"Could not fetch playlist info: {e}")
            total_videos = None
            live_playlist_title = None
        self.execute_playlist.total_playlist_videos = total_videos

        series_name = _sanitize_for_filesystem(live_playlist_title or "Unknown Series")
        print(f"Series: {series_name} ({year}), Season {season} — {total_videos or 'N/A'} episodes found")

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
        if not options:
            return False
        options['playliststart'] = start_item
        options['playlistend'] = end_item

        base_dir = os.path.dirname(options['outtmpl'])
        series_folder = f"{series_name} ({year})"
        season_folder = f"Season {season:02d}"
        episode_prefix = f"{series_name} ({year}) S{season:02d}E%(playlist_index)02d"
        options['outtmpl'] = os.path.join(
            base_dir, series_folder, season_folder,
            f"{episode_prefix} - %(title)s.%(ext)s"
        )

        self.execute_playlist.execute_core(url, options)
        return True
