# ScriptDownloader 🎬

A Python CLI tool for downloading videos from YouTube and other supported sites using `yt-dlp`.

---

## Features

- Download single videos with format selection
- Download entire playlists with range control
- Download and embed thumbnails
- Download via custom User-Agent (useful for restricted content)
- Load and process multiple URLs from a file
- Track download history (status, location, format)
- Resume or retry incomplete/failed downloads by ID
- Cross-platform: works on Linux, macOS, and Windows

---

## Requirements

- Python 3.8+
- ffmpeg (required for merging video and audio)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/alprofmahmoud/ScriptDownloader.git
cd ScriptDownloader

# Install dependencies
pip install -r requirements.txt

# Run
python main_sd.py
```

---

## Usage

### Run the script

```bash
python main_sd.py
```

### Main Menu Options

| Option | Description |
|--------|-------------|
| 1 | Show available formats for a video URL |
| 2 | Quick download (best format) |
| 3 | Download video and embed thumbnail |
| 4 | Show incomplete/failed downloads |
| 0 | Other options |

### Other Options

| Option | Description |
|--------|-------------|
| 1 | Download a playlist |
| 2 | Download using custom User-Agent |
| 3 | Load URLs from file |

### Load from File Options

| Option | Description |
|--------|-------------|
| 1 | Show formats and download from file |
| 2 | Download best format from file |
| 3 | Select format and download from file |

---

## File Structure

```
ScriptDownloader/
├── main_sd.py               # Entry point
├── config.py                # Paths configuration
├── download_core.py         # Core download logic
├── single_downloader.py     # Single video downloader
├── playlist_download.py     # Playlist downloader
├── load_urls_from_file.py   # Batch downloader from file
├── query_manager.py         # History query operations
├── display_query.py         # Terminal display/table rendering
├── requirements.txt         # Python dependencies
├── menus/
│   ├── menu.py              # Menu class
│   ├── menu_actions.py      # Menu action handlers
│   └── menu_manager.py      # Menu navigation manager
├── utils/
│   ├── status_manager.py    # Download history read/write
│   ├── formats_manager.py   # Format selection and storage
│   ├── locations_manager.py # Download location selection
│   └── validators.py        # URL validation
└── data/                    # Auto-created on first run
    ├── download_history.json
    ├── formats.txt
    ├── locations.txt
    └── pending_urls.txt
```

---

## Batch Download from File

Create a file with one URL per line:

```
https://www.youtube.com/watch?v=example1
https://www.youtube.com/watch?v=example2
https://www.youtube.com/watch?v=example3
```

Then use the **Load URLs from File** option from the menu. The script reads URLs one by one and removes each one after downloading.

---

## Download History

Every download is tracked in `data/download_history.json` with:
- Status: `downloading`, `finished`, `error`, `cancelled`, `skipped_private`, `skipped_unavailable`
- Download location
- Format ID
- Video title
- Progress percentage

You can query, resume, or delete history entries by ID from the menu.

---

## Notes

- The `data/` folder is created automatically on first run.
- File locking is used to prevent data corruption when running multiple instances simultaneously.
- Video titles are automatically cleaned (hashtags, special characters, and long titles are trimmed).
