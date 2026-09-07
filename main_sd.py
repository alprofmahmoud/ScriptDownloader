#!/usr/bin/env python3

import os
import sys
import importlib.util

from config import DATA_DIR

INSTALL_STATE_FILE = os.path.join(DATA_DIR, '.install_state.json')
REQUIRED_MODULES = ['yt_dlp', 'filelock', 'requests', 'dotenv']


def check_dependencies():
    """If install.sh already verified everything (see INSTALL_STATE_FILE),
    skip re-checking on every startup to keep it fast. Otherwise, check
    whether each required module is importable (without actually
    importing it — find_spec is cheap and doesn't run module code) and
    report exactly what's missing before the heavier imports below run."""
    if os.path.exists(INSTALL_STATE_FILE):
        return True
    missing = [m for m in REQUIRED_MODULES if importlib.util.find_spec(m) is None]
    if missing:
        print(f"Missing required libraries: {', '.join(missing)}")
        print("Run: bash install.sh")
        return False
    return True


if not check_dependencies():
    sys.exit(1)

import shutil
import traceback
from menus.menu import Menu
from menus.menu_manager import MenuManager
from menus.menu_actions import MenuActions
from playlist_download import PlaylistOption
from single_downloader import SingleDownloader
from load_urls_from_file import LoadURLsFromFile
from query_manager import QueryManager
from display_query import DisplayQuery
from subtitle_downloader import SubtitleDownloader


def create_menu():
    downloader = SingleDownloader()
    url_loader = LoadURLsFromFile()
    playlist_download = PlaylistOption()
    query_by = QueryManager()
    display_query = DisplayQuery()
    subtitle_downloader = SubtitleDownloader()

    actions = MenuActions(downloader,
                          query_by,
                          display_query,
                          url_loader,
                          playlist_download,
                          subtitle_downloader
                          )

    quick_menu = Menu(
            title="Individual Options",
            options={
                "1": "Show Format List",
                "2": "Quick Download",
                "3": "Download Thumbnails",
                "4": "Show Incomplete Downloads",
                "5": "Download Subtitles",
                "0": "Other Options",
                "e": "Exit"
            },
            actions={
                "1": actions.action_show_format,
                "2": actions.action_quick_download,
                "3": actions.action_download_thumbnails,
                "4": actions.action_query_by_status,
                "5": actions.action_download_subtitles,
                "0": actions.go_to_other_options,
                "e": actions.action_exit
            }
        )
    query_menu = Menu(
            title="Actions on Query",
            options={
                "1": "Show Completed Downloads (paged)",
                "2": "Show All Incompleted Downloads",
                "3": "Download by ID",
                "4": "Delete by ID",
                "r": "Back",
                "e": "Exit"
                },
            actions={
                "1": actions.action_query_completed_paged,
                "2": actions.action_query_all_incompleted,
                "3": actions.action_query_by_id,
                "4": actions.action_delete_by_id,
                "r": actions.go_to_back,
                "e": actions.action_exit
                }
            )
    other_menu = Menu(
            title="Other Options",
            options={
                "1": "Playlist Download",
                "2": "Download TV Series (Jellyfin Format)",
                "3": "Download by User Agent",
                "4": "Load URLs from File",
                "r": "Back",
                "e": "Exit"
            },
            actions={
                "1": actions.action_playlist_download,
                "2": actions.action_download_series_jellyfin,
                "3": actions.action_download_by_user_agent,
                "4": lambda: "switch:load_from_file",
                "r": actions.go_to_back,
                "e": actions.action_exit
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


def check_ffmpeg():
    """ffmpeg is required by yt-dlp for merging separate video/audio
    streams (needed by the 'best' format and most non-progressive
    formats). Warn clearly at startup instead of letting downloads fail
    later with a confusing yt-dlp error."""
    if shutil.which('ffmpeg') is None:
        print(
            "ffmpeg was not found on this system. Downloads that need to "
            "merge separate video/audio streams (e.g. the 'best' format) "
            "will fail. Install it, e.g. on Termux: pkg install ffmpeg"
        )
        return False
    return True


def Main():
    try:
        check_ffmpeg()

        # Sync the local history file with Supabase once at startup, so
        # every duplicate check during this run reads a local file that
        # already mirrors the cloud (see HistoryReader.sync_with_cloud).
        synced = QueryManager().sync_with_cloud()
        if synced:
            print("Cloud sync: local history is up to date with Supabase.")
        else:
            print("Cloud sync: skipped (offline or not configured) — using local history only.")

        quick_menu, query_menu, other_menu, load_menu = create_menu()

        manager = MenuManager(quick_menu, query_menu, other_menu, load_menu)
        manager.run()

    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C).")
    except Exception as e:
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        print(f"❌ Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    Main()
