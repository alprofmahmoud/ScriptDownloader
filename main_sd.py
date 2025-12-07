#!/usr/bin/env python3

import traceback
from menus.menu import Menu
from menus.menu_manager import MenuManager
from menus.menu_actions import MenuActions
from playlist_download import PlaylistOption
from single_downloader import SingleDownloader
from load_urls_from_file import LoadURLsFromFile
from query_manager import QueryManager
from display_query import DisplayQuery


def create_menu():
    downloader = SingleDownloader()
    url_loader = LoadURLsFromFile()
    playlist_download = PlaylistOption()
    query_by = QueryManager()
    display_query = DisplayQuery()

    actions = MenuActions(downloader,
                          query_by,
                          display_query,
                          url_loader,
                          playlist_download
                          )

    quick_menu = Menu(
            title="Individual Options",
            options={
                "1": "Show Format List",
                "2": "Quick Download",
                "3": "Download Thumbnails",
                "4": "Incompleted downloads",
                "0": "Other Options"
            },
            actions={
                "1": actions.action_show_format,
                "2": actions.action_quick_download,
                "3": actions.action_download_thumbnails,
                "4": actions.action_query_by_status,
                "0": actions.go_to_other_options
            }
        )
    query_menu = Menu(
            title="Actions on Query",
            options={
                "1": "Show All Incomlpeted Downloads",
                "2": "Download by ID",
                "3": "Delete by ID",
                "r": "Back"
                },
            actions={
                "1": actions.action_query_all_incompeleted,
                "2": actions.action_query_by_id,
                "3": actions.action_delete_by_id,
                "r": actions.go_to_back
                }
            )
    other_menu = Menu(
            title="Other Options",
            options={
                "1": "Playlist Download",
                "2": "Download by User Agent",
                "3": "Load URLs from File",
                "r": "Back"
            },
            actions={
                "1": actions.action_playlist_download,
                "2": actions.action_download_by_user_agent,
                "3": lambda: "switch:load from file",
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
    return quick_menu, query_menu, other_menu, load_from_file_menu


def Main():
    try:
        quick_menu, query_menu, other_menu, load_menu = create_menu()

        manager = MenuManager(quick_menu, query_menu, other_menu, load_menu)
        manager.run()

    except KeyboardInterrupt:
        print("\n🛑 Program Stopped")
    except Exception as e:
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print(f"❌ Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    Main()
