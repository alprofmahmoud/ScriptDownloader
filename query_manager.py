import json
from utils.status_manager import HistoryReader


class QueryManager(HistoryReader):
    def __init__(self):
        super().__init__()

    def query_by_url(self, url):
        # Return None if URL is empty
        if not url:
            return None
        # Read all download history
        all_downloads = self._read_history()
        # Search in regular URLs (single videos)
        for entry in all_downloads:
            if entry.get('url') == url:
                return {
                    'id': entry.get('id'),
                    'location': entry.get('location')
                }
        # Search for playlist URLs
        for entry in all_downloads:
            if entry.get('playlist_url') == url:
                videos = entry.get('videos', [])
                downloaded_count = sum(
                    1 for v in videos if v.get('status') == 'finished'
                )
                # Use the location of any video that already has one saved
                location = next(
                    (v.get('location') for v in videos if v.get('location')),
                    None
                )
                return {
                    'id': entry.get('id'),
                    'playlist_title': entry.get('playlist_title'),
                    'total_videos': entry.get('total_videos'),
                    'downloaded_count': downloaded_count,
                    'location': location,
                    'is_playlist': True
                }
        # Search in playlist videos
        for entry in all_downloads:
            if 'videos' in entry:
                for video in entry['videos']:
                    if video.get('url') == url:
                        return {
                            'id': entry.get('id'),
                            'total_videos': entry.get('total_videos'),
                            'location': video.get('location'),
                            'playlist_index': video.get('playlist_index')
                        }
        # URL not found
        return None

    def query_by_video_id(self, video_id):
        """Thin wrapper around HistoryReader.find_by_video_id, used by the
        pre-download duplicate check."""
        return self.find_by_video_id(video_id)

    def query_by_status(self, status=None, statuses=None):
        all_downloads = self._read_history()
        matching_entries = []
        has_playlist = False
        if statuses is not None:
            # If passed statuses list → use them
            target_statuses = statuses
        elif status is not None:
            # If passed single status → convert to list
            target_statuses = [status]
        else:
            # If nothing passed → default
            target_statuses = ["downloading"]
        for entry in all_downloads:
            entry_status = entry.get('status', None)
            if entry_status in target_statuses:
                filtered_entry = {}
                filtered_entry['id'] = entry.get('id')
                if 'playlist_count' in entry:
                    filtered_entry['playlist_url'] = entry.get('playlist_url')
                else:
                    filtered_entry['url'] = entry.get('url', 'N/A')
                filtered_entry['status'] = entry.get('status', 'N/A')
                filtered_entry['percent_str'] = entry.get('percent_str', 'N/A')
                if 'playlist_count' in entry:
                    # The playlist's overall progress must be based on how
                    # many of its videos actually finished downloading, not
                    # on the total video count (playlist_count/total_videos
                    # are both "totals" and were being divided by each
                    # other before, which is why progress showed ~100%
                    # for every playlist regardless of real progress).
                    videos = entry.get('videos', [])
                    downloaded_count = sum(
                        1 for v in videos if v.get('status') == 'finished'
                    )
                    filtered_entry['downloaded_count'] = downloaded_count
                    filtered_entry['playlist_count'] = entry.get('playlist_count')
                    filtered_entry['total_videos'] = entry.get('total_videos')
                    has_playlist = True
                matching_entries.append(filtered_entry)
        return {
                'entries': matching_entries,
                'has_playlist': has_playlist
                }

    def query_by_id(self):
        try:
            id_query: int = int(input("Enter Id: ").strip())
            if not id_query:
                print("ID cannot be empty")
                return None
            item_download = self._read_history()
            for item in item_download:
                item_id = item.get('id')
                if isinstance(item_id, int):
                    search_id = int(id_query)
                else:
                    search_id = id_query

                if item_id == search_id:
                    url = item.get('url')
                    location = item.get('location')
                    format_id = item.get('format_id')
                    return url, format_id, location
            print(f"Item with ID '{id_query}' not found")
            return None
        except ValueError:
            print("Invalid ID format")
            return None

    def delete_by_id(self):
        """Delete item from history by ID"""
        try:
            # Read ID integer from user
            item_id: int = int(input("Enter ID to Delete: "))
            # Read data (from parent class)
            data = self._read_history()
            # Delete item
            original_length = len(data)
            updated_data = [item for item in data if item.get('id') != item_id]
            # Verify deletion
            if len(updated_data) == original_length:
                print(f"❌ ID {item_id} not found")
                return False
            # Save updated data
            result = self._write_history(updated_data)
            # امسح السطر من Supabase كمان (لو مكتوبش هنا، هيرجع تاني عند أول قراءة)
            self._sync_delete(item_id)
            print(f"Deleted item with ID: {item_id}")
            return result
        except ValueError:
            print("❌ Must be a number!")
        except Exception as e:
            print(f"❌ Error deleting item: {e}")
            return False
