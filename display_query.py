import re
from utils.pager import page_text
from utils.locations_manager import shorten_path_for_display


class DisplayQuery:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    def __init__(self, width=40):
        self.width = width

    def _get_visible_length(self, text):
        text = str(text)
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        clean_text = ansi_escape.sub('', text)
        return len(clean_text)

    def _colorize(self, text, color):
        return f"{color}{text}{self.RESET}"

    def _strip_colors(self, text):
        text = str(text)
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        clean_text = ansi_escape.sub('', text)
        return clean_text

    def show_single(self, query_result=None):
        id_val = query_result.get('id', 'N/A')
        location = shorten_path_for_display(query_result.get('location', 'N/A'))
        id_length = len(str(id_val))
        status_text = "Found in 📁 "
        content = f"{status_text}{location}"
        length_content = len(content)
        horizontal_line = self._create_horizontal_line(id_length)
        padding = self._calculate_padding(length_content)
        row = f"| {self.BLUE}{id_val}{self.RESET} | {content}{' '*padding}|"
        self._print_box(horizontal_line, row)

    def show_from_file(self, query_result, total_urls):
        id_val = query_result.get('id', 'N/A')
        location = shorten_path_for_display(query_result.get('location', 'N/A'))
        id_length = len(str(id_val))
        total_text = f" (Total: {self.GREEN}{total_urls}{self.RESET} URLs)"
        status_text = "Found in 📁 "
        content = f"{status_text}{location}{total_text}"
        content_length = self._get_visible_length(content)
        horizontal_line = self._create_horizontal_line(id_length)
        padding = self._calculate_padding(content_length)
        row = f"| {self.BLUE}{id_val}{self.RESET} | {content}{' '*padding}|"
        self._print_box(horizontal_line, row)

    def show_playlist(self, query_result):
        id_val = query_result.get('id', 'N/A')
        playlist_title = query_result.get('playlist_title', 'N/A')
        location = query_result.get('location') or 'not chosen yet'
        downloaded_count = query_result.get('downloaded_count', 0)
        total_videos = query_result.get('total_videos', 'N/A')
        id_length = len(str(id_val))
        status_text = "Found in 📁"
        location_cuting = self._truncate_text(location, 14)
        colored_downloaded = self._colorize(downloaded_count, self.CYAN)
        colored_total = self._colorize(total_videos, self.GREEN)
        index_text = f"{playlist_title}: {colored_downloaded} of {colored_total} downloaded"
        content = f"{status_text} {location_cuting} — {index_text}"
        length_content = self._get_visible_length(content)
        horizontal_line = self._create_horizontal_line(id_length, width=50)
        padding = self._calculate_padding(length_content, width=50)
        colored_id = self._colorize(id_val, self.BLUE)
        row = f"| {colored_id} | {content}{' ' * padding}|"
        self._print_box(horizontal_line, row)

    def show_not_found(self, new_id=None, total_urls=None):
        status_text = "Not found"
        if new_id is not None:
            id_length = len(str(new_id))
            if total_urls is not None:
                colored_total_urls = self._colorize(total_urls, self.GREEN)
                total_text = f"(Total: {colored_total_urls} URLs)"
                content = f"{status_text} {total_text}"
                content_length = self._get_visible_length(content)
                horizontal_line = self._create_horizontal_line(id_length)
                padding = self._calculate_padding(content_length)
                colored_id = self._colorize(new_id, self.BLUE)
                row = f"| {colored_id} | {content}{' ' * padding} |"
            else:
                content_length = len(status_text)
                horizontal_line = self._create_horizontal_line(id_length)
                padding = self._calculate_padding(content_length)
                colored_id = self._colorize(new_id, self.BLUE)
                row = f"| {colored_id} | {status_text}{' ' * padding} |"
            self._print_box(horizontal_line, row)
        else:
            content_length = len(status_text)
            padding = self.width - content_length - 2
            horizontal_line = f"+{'-' * self.width}+"
            row = f"|{status_text}{' ' * padding}|"
            print(horizontal_line)
            print(row)
            print(horizontal_line)

    def show_downloads_table(self, query_result):
        """Print the downloads table directly to the terminal (unchanged
        behavior)."""
        lines = self._build_downloads_table_lines(query_result)
        if lines is None:
            print("No downloads found with the specified status.")
            return
        for line in lines:
            print(line)

    def page_downloads_table(self, query_result, title=None):
        """Render the downloads table in the exact same format as
        show_downloads_table, but display it through a 'less'-style
        pager instead of printing straight to the terminal. Useful for
        long histories (e.g. all completed downloads)."""
        lines = self._build_downloads_table_lines(query_result)
        if lines is None:
            print("No downloads found with the specified status.")
            return
        text_blocks = []
        if title:
            text_blocks.append(f"{self.BOLD}{title}{self.RESET}\n")
        text_blocks.append("\n".join(lines))
        page_text("\n".join(text_blocks))

    def _build_downloads_table_lines(self, query_result):
        """Build the downloads table as a list of formatted lines
        (same layout/columns/colors as before), without printing them.
        Returns None if there are no entries to show."""
        downloads_list = query_result.get('entries', [])
        has_playlist = query_result.get('has_playlist', False)
        if not downloads_list:
            return None
        # Calculate width for every column
        widths = self._calculate_column_widths(downloads_list, has_playlist)
        id_width = widths['id']
        url_width = widths['url']
        status_width = widths['status']
        percent_width = widths['percent']
        if has_playlist:
            index_width = widths.get('index', 8)
            total_width = widths.get('total', 8)
        # Build separator
        id_separator = '-' * (id_width + 2)
        url_separator = '-' * (url_width + 2)
        status_separator = '-' * (status_width + 2)
        percent_separator = '-' * (percent_width + 2)
        if has_playlist:
            # Build separator for playlist table (6 columns)
            index_separator = '-' * (index_width + 2)
            total_separator = '-' * (total_width + 2)
            separator = (
                    f"+{id_separator}+{url_separator}+{status_separator}"
                    f"+{percent_separator}+{index_separator}"
                    f"+{total_separator}+"
                    )
        else:
            separator = (f"+{id_separator}+{url_separator}+{status_separator}"
                         f"+{percent_separator}+"
                         )
        # Build header
        if has_playlist:
            header = (
                f"| {'ID':^{id_width}} "
                f"| {'URL':^{url_width}} "
                f"| {'Status':^{status_width}} "
                f"| {'Progress':^{percent_width}} "
                f"| {'Done':^{index_width}} "
                f"| {'Total':^{total_width}} |"
            )
        else:
            header = (
                f"| {'ID':^{id_width}} "
                f"| {'URL':^{url_width}} "
                f"| {'Status':^{status_width}} "
                f"| {'Progress':^{percent_width}} |"
                )

        lines = [separator, header, separator]
        for item in downloads_list:
            # Extract info
            id_val = item.get('id', 'N/A')
            url = item.get('url') or item.get('playlist_url')
            status = item.get('status', 'N/A')
            # Truncate URL if longer than column width
            truncated_url = self._truncate_text(url, url_width)
            if has_playlist and 'playlist_count' in item:
                # Playlist entry: progress is downloaded videos / total videos
                downloaded_count = item.get('downloaded_count', 0)
                total = item.get('total_videos') or item.get('playlist_count') or 'N/A'
                if isinstance(total, (int, float)) and total > 0:
                    percentage = (downloaded_count / total) * 100
                    percent = f"{percentage:.1f}%"
                else:
                    percent = 'N/A'
                row = (
                    f"| {id_val:^{id_width}} "
                    f"| {truncated_url:<{url_width}} "
                    f"| {status:<{status_width}} "
                    f"| {percent:^{percent_width}} "
                    f"| {downloaded_count:^{index_width}} "
                    f"| {total:^{total_width}} |"
                )
            else:
                # Use existing data for regular entries
                percent = item.get('percent_str')
                if has_playlist:
                    row = (
                        f"| {id_val:^{id_width}} "
                        f"| {truncated_url:<{url_width}} "
                        f"| {status:<{status_width}} "
                        f"| {percent:^{percent_width}} "
                        f"| {'-':^{index_width}} "
                        f"| {'-':^{total_width}} |"
                    )
                else:
                    row = (
                        f"| {id_val:^{id_width}} "
                        f"| {truncated_url:<{url_width}} "
                        f"| {status:<{status_width}} "
                        f"| {percent:^{percent_width}} |"
                    )
            lines.append(row)
        lines.append(separator)
        return lines

    def _truncate_text(self, text, max_length):
        text = str(text)
        if len(text) <= max_length:
            return text
        if max_length < 4:
            return text[:max_length]
        truncated = text[7:7 + (max_length - 3)]
        return truncated + "..."

    def _create_horizontal_line(self, id_length, width=None):
        if width is None:
            width = self.width
        left = '-' * (id_length + 2)
        right = '-' * width
        horizontal_line = f"+{left}+{right}+"
        return horizontal_line

    def _calculate_padding(self, content_length, width=None):
        if width is None:
            width = self.width
        padding = width - content_length - 2
        if padding < 0:
            padding = 0
        return padding

    def _print_box(self, horizontal_line, row):
        print(horizontal_line)
        print(row)
        print(horizontal_line)

    def _calculate_column_widths(self, downloads_list, has_playlist=False):
        if not downloads_list:
            default_widths = {
                'id': 2,
                'status': 6,
                'percent': 8,
                'url': 30
            }
            if has_playlist:
                default_widths['index'] = 8
                default_widths['total'] = 8
            return default_widths
        # Initialize max length trackers
        max_id_length = 0
        max_status_length = 0
        max_percent_length = 0
        max_url_length = 0
        if has_playlist:
            max_index_length = 0
            max_total_length = 0
        # Calculate the longest value for each column
        for item in downloads_list:
            # 1️⃣ Calculate ID length
            id_val = str(item.get('id', 'N/A'))
            current_id_length = len(id_val)
            if current_id_length > max_id_length:
                max_id_length = current_id_length
            # 2️⃣ Calculate Status length
            status_val = item.get('status', 'N/A')
            current_status_length = len(status_val)
            if current_status_length > max_status_length:
                max_status_length = current_status_length
            # 3️⃣ Calculate Percent length
            percent_val = item.get('percent_str', '0%')
            current_percent_length = len(percent_val)
            if current_percent_length > max_percent_length:
                max_percent_length = current_percent_length
            # 4️⃣ Calculate URL length
            # Note: URL could be 'url' or 'playlist_url'
            url_val = item.get('url') or item.get('playlist_url', 'N/A')
            current_url_length = len(str(url_val))
            if current_url_length > max_url_length:
                max_url_length = current_url_length
            # 5️⃣ If there's a playlist, calculate additional columns
            if has_playlist:
                # Calculate Index length (playlist_count)
                if 'playlist_count' in item:
                    index_val = str(item.get('playlist_count', 'N/A'))
                    current_index_length = len(index_val)
                    if current_index_length > max_index_length:
                        max_index_length = current_index_length
                # Calculate Total length (total_videos)
                if 'total_videos' in item:
                    total_val = str(item.get('total_videos', 'N/A'))
                    current_total_length = len(total_val)
                    if current_total_length > max_total_length:
                        max_total_length = current_total_length
        # Ensure minimum width
        max_id_length = max(max_id_length, 2)
        max_status_length = max(max_status_length, 6)
        max_percent_length = max(max_percent_length, 8)
        # Set URL width with max cap
        url_width = min(max_url_length, 25)
        # Ensure minimum width for playlist columns
        if has_playlist:
            max_index_length = max(max_index_length, 8)
            max_total_length = max(max_total_length, 8)
        # Build the return dictionary
        widths = {
            'id': max_id_length,
            'status': max_status_length,
            'percent': max_percent_length,
            'url': url_width
        }
        # Add playlist columns if needed
        if has_playlist:
            widths['index'] = max_index_length
            widths['total'] = max_total_length

        return widths
