#!/usr/bin/env python3

import json
import os
from typing import Optional, Dict, Any, List


class StatusManager:
    def __init__(self, status_file='./download_history_file.json'):
        self.status_file = status_file

    def _read_history(self) -> List[Dict[str, Any]]:
        # Read existing data
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                try:
                    all_downloads = json.load(f)
                except json.JSONDecodeError:
                    all_downloads = []
        else:
            all_downloads = []
        return all_downloads

    def _generate_id(self) -> int:
        # Generate sequential ID for new entry
        all_downloads = self._read_history()
        if not all_downloads:
            return 1
        # Get the largest existing ID and add 1 to it
        max_id = max(entry.get('id', 0) for entry in all_downloads)
        return max_id + 1

    def update_status_by_url(self, url, new_status,
                             percent_str='0%',
                             output_location=None,
                             format_id=None,
                             video_title=None,
                             extra_info=None):
        # Update status for existing URL or add new entry if not found
        if not url:
            return
        # Read existing data
        all_downloads = self._read_history()

        # Search for URL and update if found
        found = False
        for entry in all_downloads:
            if entry.get('url') == url:
                entry['status'] = new_status  # Update status
                entry['percent_str'] = percent_str
                if output_location is not None:
                    entry['location'] = output_location
                found = True
                entry['format_id'] = format_id
                entry['video_title'] = video_title
                break
        # If not found, add new entry
        if not found:
            all_downloads.append({
                'id': self._generate_id(),
                'url': url,
                'status': new_status,
                'percent_str': percent_str,
                'location': output_location,
                'format_id': format_id,
                'video_title': video_title
            })
        # Save back to file
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(all_downloads, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False

    def update_status_by_url_playlist(self,
                                      playlist_url,
                                      video_url,
                                      new_status,
                                      percent_str='0%',
                                      output_location=None,
                                      format_id=None,
                                      video_title=None,
                                      extra_info=None,
                                      ):
        # Update status for existing URL or add new entry if not found
        if not playlist_url or not video_url:
            return
        # Read existing data
        all_downloads = self._read_history()
        # Extract info from extra_info
        extra_info = extra_info or {}
        playlist_title = extra_info.get('playlist_title')
        total_videos = extra_info.get('total_playlist_videos')
        playlist_index = extra_info.get('playlist_index')
        playlist_count = extra_info.get('playlist_count')
        filename = extra_info.get('filename')
        # Search for URL and update if found
        # Search for playlist entry
        playlist_found = False
        for entry in all_downloads:
            if entry.get('playlist_url') == playlist_url:
                playlist_found = True
                # Update playlist info
                if playlist_title:
                    entry['playlist_title'] = playlist_title
                if total_videos:
                    entry['total_videos'] = total_videos
                if playlist_count:
                    entry['playlist_count'] = playlist_count
                # Get or create videos array
                if 'videos' not in entry:
                    entry['videos'] = []
                # Search for video inside playlist
                video_found = False
                for video in entry['videos']:
                    if video.get('url') == video_url:
                        # Update existing video
                        video['status'] = new_status
                        video['percent_str'] = percent_str
                        video['video_title'] = video_title
                        video['format_id'] = format_id
                        if output_location:
                            video['location'] = output_location
                        if filename:
                            video['filename'] = filename
                        if playlist_index is not None:
                            video['playlist_index'] = playlist_index
                        video_found = True
                        break
                # If video not found, add it
                if not video_found:
                    entry['videos'].append({
                        'url': video_url,
                        'video_title': video_title,
                        'status': new_status,
                        'percent_str': percent_str,
                        'format_id': format_id,
                        'location': output_location,
                        'filename': filename,
                        'playlist_index': playlist_index
                    })
                # Update overall playlist status
                entry['status'] = self._calculate_playlist_status(
                            entry['videos'])
                break
        # If playlist not found, create new entry
        if not playlist_found:
            all_downloads.append({
                'id': self._generate_id(),
                'playlist_url': playlist_url,
                'playlist_title': playlist_title,
                'total_videos': total_videos,
                'playlist_count': playlist_count,
                'status': new_status,
                'videos': [{
                    'url': video_url,
                    'video_title': video_title,
                    'status': new_status,
                    'percent_str': percent_str,
                    'format_id': format_id,
                    'location': output_location,
                    'filename': filename,
                    'playlist_index': playlist_index
                }]
            })
        # Save back to file
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(all_downloads, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False

    def _calculate_playlist_status(self, videos):
        """Calculate overall playlist status based on videos."""
        if not videos:
            return 'queued'
        statuses = [v.get('status') for v in videos]
        if all(s == 'finished' for s in statuses):
            return 'finished'
        if any(s == 'downloading' for s in statuses):
            return 'downloading'
        if any(s == 'failed' for s in statuses):
            return 'failed'
        return 'queued'
