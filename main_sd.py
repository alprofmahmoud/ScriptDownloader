#!/usr/bin/env python3

import traceback
from menu import Menu
from menu_manager import MenuManager
from menu_actions import MenuActions
from playlist_download import PlaylistOption
from single_downloader_mode_sd import SingleDownloader
from load_urls_from_file import LoadURLsFromFile


def create_menu():
    downloader = SingleDownloader()
    url_loader = LoadURLsFromFile()
    playlist_download = PlaylistOption()

    actions = MenuActions(downloader, url_loader, playlist_download)

    quick_menu = Menu(
            title="Individual Options",
            options={
                "1": "Show Format List",
                "2": "Quick Download",
                "3": "Download Thumbnails",
                "0": "Other Options"
            },
            actions={
                "1": actions.action_show_format,
                "2": actions.action_quick_download,
                "3": actions.action_download_thumbnails,
                "0": actions.go_to_other_options
            }
        )
    other_menu = Menu(
            title="Other Options",
            options={
                "1": "Playlist Download",
                "2": "Load URLs from File",
                "r": "Back"
            },
            actions={
                "1": actions.action_playlist_download,
                "2": lambda: "switch:load from file",
                "r": actions.go_to_back
            }
        )

    load_from_file_menu = Menu(
            title="Load URLs from File Options",
            options={
                "1": "Show Formats and Download",
                "2": "Download Best Format",
                "3": "Select Format",
                "r": "Back"
            },
            actions={
                "1": actions.action_show_formats_from_file,
                "2": actions.action_download_best_from_file,
                "3": actions.action_download_with_format,
                "r": actions.go_to_back
            }
        )
    return quick_menu, other_menu, load_from_file_menu


def Main():
    try:
        quick_menu, other_menu, load_menu = create_menu()

        manager = MenuManager(quick_menu, other_menu, load_menu)
        manager.run()

    except KeyboardInterrupt:
        print("\n🛑 Program Stopped")
    except Exception as e:
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print(f"❌ Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    Main()
