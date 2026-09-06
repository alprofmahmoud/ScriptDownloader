# Changelog — ScriptDownloader

This file documents every code change made in this working session, written
as detailed commit messages. All new/edited code comments are in English.

---

## commit 1 — feat(history): track video_id and skip duplicate downloads

**Files changed:** `utils/status_manager.py`, `query_manager.py`,
`download_core.py`, `single_downloader.py`

**What changed:**
- `video_id` is now stored on every history entry, both for single videos
  and for videos nested inside a playlist (`update_status_by_url`,
  `update_status_by_url_playlist`).
- Added `HistoryReader.find_by_video_id(video_id)`: looks up a video by its
  id across both regular entries and nested playlist videos, returns its
  storage location and status.
- Added `QueryManager.query_by_video_id(video_id)` as a thin public wrapper
  around the above.
- Added `DownloadCore.probe_video_info(url)`: uses yt-dlp with
  `skip_download=True` to fetch `id` / `title` / `uploader` / `upload_date`
  *before* any actual download starts.
- Added `DownloadCore._resolve_outtmpl(video_info, stored_location)`: if a
  file with the default computed name already exists on disk but is *not*
  tracked in history, the output filename is disambiguated using
  `uploader + upload_date (as epoch seconds)` instead of silently
  overwriting the existing file.
- `single_downloader.py` now probes the video first, checks history by
  `video_id`, and skips the download entirely (printing where it's already
  stored) if a match is found.

**Why:** avoid re-downloading videos that are already in history, and avoid
silently overwriting unrelated local files that happen to share a name.

---

## commit 2 — feat(sync): real two-way local/cloud sync, local-only duplicate checks

**Files changed:** `utils/status_manager.py`, `main_sd.py`

**What changed:**
- Added `HistoryReader.sync_with_cloud()`: pulls all rows from Supabase,
  merges them into the local JSON file (cloud wins on id conflicts, since
  it's the shared source of truth across devices), then pushes back any
  local-only entries that were never successfully synced (e.g. because of
  an earlier permissions/auth failure).
- This is called once automatically at startup, in `main_sd.py`'s `Main()`,
  before any menu is shown.
- `find_by_video_id()` now reads from the local file only (`_read_local()`
  instead of `_read_history()`). Since the sync above already ran at
  startup, the local file is a mirror of the cloud by the time any
  duplicate check happens — keeping the per-download check fast and free
  of a network round-trip.
- Removed the "⚠️" warning icon from all Supabase-related warning messages
  in `status_manager.py`, `download_core.py`, and `single_downloader.py`;
  they now print plain text only.

**Why:** the previous read logic only *preferred* cloud data when
available — it never actually merged local-only entries back up, so items
that failed to push during a permissions outage stayed stuck locally
forever unless `migrate_history.py` was run by hand.

---

## commit 3 — fix(playlist): progress percentage was computed from the wrong numbers

**Files changed:** `query_manager.py`, `display_query.py`

**What changed:**
- `query_by_status()` now computes `downloaded_count` (videos with
  `status == 'finished'` inside `entry['videos']`) for playlist entries.
- `display_query.py`'s table renderer now computes playlist progress as
  `downloaded_count / total_videos`, instead of the old
  `playlist_count / total_videos`.
- Renamed the "Index" table column to "Done" to reflect what it now shows.

**Why:** `playlist_count` and `total_videos` were both "total number of
videos in the playlist" (just populated from two different code paths),
so the old formula was effectively `total / total`, which showed close to
100% progress almost immediately regardless of how many videos had
actually finished downloading.

**Note:** the nested-videos-per-playlist data structure itself
(`entry['videos']`), and showing a single row for the playlist URL in the
table, already existed before this session — only the percentage math was
broken.

---

## commit 4 — feat(formats): add H.264/m4a "best" format selector

**Files changed:** `utils/formats_manager.py`

**What changed:**
- `_get_best_format()` now returns
  `bv*[vcodec^=avc1]+ba[ext=m4a]/bv*+ba/best` instead of the literal string
  `"best"`. This prefers H.264 video + m4a audio (maximum player/device
  compatibility), falling back to yt-dlp's own best-quality selection if
  no avc1 stream is available.
- The format-selection menu still displays the option as **"best"** to the
  user — the menu label and the actual value sent to yt-dlp are now
  decoupled, so the underlying selector can change without affecting the
  UI.

---

## commit 5 — chore(setup): add install.sh

**Files added:** `install.sh`

**What it does:**
- Detects an existing active virtual environment (`$VIRTUAL_ENV`); if none
  is active, creates `.venv` in the project root (or reuses it if it
  already exists) and activates it.
- Never installs anything into the system/global Python — everything goes
  into the venv.
- Checks each package in `requirements.txt` individually via
  `pip show`, and only installs the ones that are actually missing.
- Also checks/installs `pg8000` and `certifi`, needed by the one-time
  Supabase admin scripts (`fix_permissions.py`, `migrate_history.py`).

---

## commit 6 — perf(download): stop extracting video info twice per download

**Files changed:** `download_core.py`, `single_downloader.py`

**What changed:**
- `probe_video_info()` now returns the *full* raw yt-dlp info dict instead
  of a small trimmed copy of it.
- `execute_core()` accepts an optional `preloaded_info` argument. When
  provided, it downloads via `ydl.process_ie_result(preloaded_info,
  download=True)`, reusing the info already fetched during the
  pre-download probe, instead of extracting the same page a second time.
- If reusing the cached info fails (e.g. expired CDN links on sites like
  TikTok/Instagram, if enough time passed between the probe and the
  download menus), it falls back to a normal fresh `ydl.download([url])`.
- `single_downloader.py` now passes the probed info into `execute_core()`.

**Why:** the duplicate-check probe added in commit 1 was fetching/parsing
every page once for the check and then a second time for the actual
download, roughly doubling the time (and extractor error surface) per
download. This makes it fetch the page once in the common case.

---

## commit 7 — fix(display): show download locations relative to home

**Files changed:** `utils/locations_manager.py`, `display_query.py`,
`single_downloader.py`

**What changed:**
- Added `shorten_path_for_display()` in `utils/locations_manager.py`:
  paths inside the user's home directory are shown relative to it (e.g.
  `/data/data/com.termux/files/home/Downloads` → `/Downloads`); paths
  outside the home directory are shown unchanged.
- The location-selection menu, the "Found in" status messages, and the
  "already downloaded" duplicate-check message now use this shortened
  label for display only — the actual value used for downloading/history
  storage is still the full absolute path, unchanged.

---

## commit 8 — fix(formats): cap 'best' at 720p

**Files changed:** `utils/formats_manager.py`

**What changed:**
- `_get_best_format()` now returns
  `bv*[vcodec^=avc1][height<=720]+ba[ext=m4a]/bv*[height<=720]+ba/best[height<=720]`.
- Added a `[height<=720]` constraint on every fallback path (avc1 path,
  generic video+audio path, and the final `best` fallback), so the "best"
  choice never selects a resolution above 720p even if a higher one
  (e.g. 1080p) is available.

---

## commit 9 — perf(history): stop hitting Supabase on every progress tick

**Files changed:** `utils/status_manager.py`

**What changed:**
- `update_status_by_url()` and `update_status_by_url_playlist()` now read
  from the local file (`_read_local()`) instead of `_read_history()`.
- Reduced `REQUEST_TIMEOUT` from 8 to 4 seconds.

**Why:** these two functions run on every yt-dlp progress-hook tick —
many times per second during a single download. `_read_history()` calls
`_supabase_select_all()`, a full HTTP GET of the entire history table, on
every call, with no throttling (unlike the push side, which was already
throttled). This was the main cause of the tool feeling slow, especially
on mobile networks — every progress update was blocked on a full network
round-trip. Since `sync_with_cloud()` (commit 2) already mirrors Supabase
into the local file once at startup, and pushes remain throttled, reading
locally here is both correct and fast. The lower timeout also reduces how
long Ctrl+C can appear to "hang" if pressed while a push happens to be in
flight (Python cannot interrupt a blocking network call mid-request).

---

## commit 10 — fix(playlist): show real title/total/location instead of N/A

**Files changed:** `playlist_download.py`, `query_manager.py`,
`display_query.py`

**What changed:**
- `playlist_download.py` now fetches the playlist's live info (title +
  total video count via `extract_flat`) **before** showing the status
  line, instead of after. Previously the status line was built purely
  from whatever was already saved in history for that URL — if an earlier
  attempt had created an entry before that metadata was captured, every
  later run kept showing "N/A" forever, since nothing re-checked it.
- `query_manager.py`'s `query_by_url()` (playlist branch) now also
  returns `downloaded_count` (videos with `status == 'finished'` in the
  entry) and `location` (pulled from any nested video that already has
  one saved).
- `display_query.py`'s `show_playlist()` was fixed to use these fields
  correctly — previously the `location` variable was actually holding
  `playlist_title` (a leftover naming mix-up), so the folder location was
  never actually shown. It now prints the real save location, and
  "X of Y downloaded" using the live total instead of a stale saved
  index.

---

## commit 11 — fix(probe): stop double-printing the same extractor error

**Files changed:** `download_core.py`

**What changed:**
- Added a `_SilentLogger` passed as `'logger'` in `probe_video_info()`'s
  yt-dlp options, suppressing yt-dlp's own console output during the
  probe.
- The `except` block's message is now trimmed to the first line and the
  "please report this issue..." boilerplate is stripped for readability.

**Why:** yt-dlp's `quiet` option does not suppress error-level messages —
only info/warnings. So a failing probe (e.g. the TikTok extractor issue)
was printing yt-dlp's own `ERROR: [TikTok] ...` line *and* our own
`Could not probe video info before download: ...` message with the same
(often long) text right after it.

---

## commit 12 — chore(ux): unify exit/interrupt messages

**Files changed:** `utils/exit_handler.py`, `menus/menu_manager.py`,
`main_sd.py`

**What changed:**
- Replaced three different, inconsistent exit/interrupt messages
  (`"Exit 🛑"`, `"👋 Exiting program..."`, `"🛑 Program Stopped"`) with one
  consistent message per situation (normal exit, Ctrl+C, back-to-main).



---

## commit 13 — chore(ux): review menu placement, consistent incomplete-downloads filter

**Files changed:** `main_sd.py`, `menus/menu_actions.py`, `utils/locations_manager.py`

**What changed:**
- Renamed the main menu's "Incompleted downloads" to "Show Incomplete
  Downloads".
- Unified the "incomplete" definition: the main menu entry now queries
  `["error", "downloading"]` (same as the query submenu's own "Show All
  Incompleted Downloads"), instead of `"downloading"` only — previously
  the two entry points showed different subsets under similar labels.
- Reordered the query submenu to: 1) Show Completed Downloads (paged),
  2) Show All Incompleted Downloads, 3) Download by ID, 4) Delete by ID.
- `shorten_path_for_display()` no longer keeps the leading path
  separator (`/Downloads` -> `Downloads`).

---

## commit 14 — feat(playlist): download TV series with Jellyfin naming

**Files changed:** `playlist_download.py`, `menus/menu_actions.py`,
`main_sd.py`

**What changed:**
- Added `PlaylistOption.download_series_jellyfin()`: asks for the URL,
  then the series year, then the season number (in that order), fetches
  the playlist title automatically to use as the series name, and
  downloads into Jellyfin's expected layout:
  `Series Name (Year)/Season 01/Series Name (Year) S01E03 - Title.ext`.
- Added `_sanitize_for_filesystem()` to strip characters that are invalid
  in folder/file names from the auto-fetched series title.
- New "Other Options" menu entry: **"Download TV Series (Jellyfin
  Format)"** (option 2, right after Playlist Download).

---

## commit 15 — feat(startup): ffmpeg check + clearer offline/cloud-sync status

**Files changed:** `main_sd.py`, `utils/status_manager.py`

**What changed:**
- Added `check_ffmpeg()` in `main_sd.py`, run at startup: warns clearly
  (with the Termux install command) if `ffmpeg` is missing, instead of
  letting downloads fail later with a confusing yt-dlp error.
- Startup now prints one explicit summary line after the cloud sync
  attempt: either "local history is up to date with Supabase" or
  "skipped (offline or not configured) — using local history only".
- The "SUPABASE_URL / SUPABASE_KEY not found" message now also prints
  the exact `.env` path it looked for, to make it obvious when the tool
  is being run from the wrong project directory (a real case that came
  up: `~/ScriptDownloader` vs `~/downloads/ScriptDownloader-main`, only
  one of which had `.env`).

---

## commit 16 — chore(cleanup): dedupe load_urls_from_file.py

**Files changed:** `load_urls_from_file.py`

**What changed:**
- Merged `show_formats_list_urls_from_file_and_download()`,
  `downloader_from_file_best_format()`, and
  `downloader_from_file_with_select_format()` into one shared
  `_process_urls_from_file(options_mode, fixed_options, show_format_list)`
  helper. The three public methods are now thin wrappers that call it
  with different parameters. Behavior is unchanged; ~20 lines of
  duplicated loop/validation logic removed.

**Note on the error/failed status bug:** already fixed earlier in commit
3 (`_calculate_playlist_status` unified on `'error'`, matching what
`download_core.py` actually records) — re-checked the whole codebase this
round and confirmed no remaining `'failed'` usages anywhere.


---

**Usage (commit 5 — install.sh):**
```bash
bash install.sh
```

---

## commit 17 — feat(subtitles): download subtitles with language selection

**Files added:** `subtitle_downloader.py`
**Files changed:** `menus/menu_actions.py`, `main_sd.py`

**What changed:**
- Added `SubtitleDownloader.download_subtitles()`: asks for the URL,
  fetches and lists all available subtitles (manual first, then
  auto-generated ones not already covered), lets the user pick one by
  number, then downloads it in the best format the site offers
  (`subtitlesformat: 'best'`) into a chosen location.
- New main-menu entry: **"Download Subtitles"** (option 5, right after
  "Show Incomplete Downloads").

---

## commit 18 — perf(startup): skip dependency re-checking after install.sh

**Files changed:** `install.sh`, `main_sd.py`

**What changed:**
- `install.sh` now writes `data/.install_state.json` (`{"verified": true}`)
  after all dependencies are confirmed installed.
- `main_sd.py` now checks for that marker file **before** importing any
  third-party-dependent modules. If present, it skips the dependency
  check entirely (fast startup path, as requested). If absent, it checks
  each required module's availability via `importlib.util.find_spec`
  (which doesn't actually import/run the module, so it's cheap) and
  prints exactly which ones are missing, then exits with a clear message
  instead of a raw `ModuleNotFoundError` traceback.
- `data/` was already covered by `.gitignore`, so the new marker file
  (and the existing `download_history.json` / `.lock` file) are not
  committed to the repo.
