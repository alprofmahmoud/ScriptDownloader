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

    def update_status_by_url(self, url, new_status, output_location=None):
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
                if output_location is not None:
                    entry['location'] = output_location
                found = True
                break
        
        # If not found, add new entry
        if not found:
            all_downloads.append({
                'id': self._generate_id(),
                'url': url,
                'status': new_status,
                'location': output_location
            })
        # Save back to file
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(all_downloads, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False


