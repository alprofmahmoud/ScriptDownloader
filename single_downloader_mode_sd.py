#!/usr/bin/env python3

import yt_dlp
from typing import Optional, Dict, Any, List
from utils.validators import _is_valid_url_format, get_valid_url
from utils.status_manager import StatusManager
from utils.select_output_location import select_output_location

class SingleDownloader:
    def __init__(self, url=None, required_video_quality=None):
        self.url = url
        self.required_video_quality = required_video_quality
        self.status_manager = StatusManager('./download_history_file.json')
        self.download_status = None
        self.output_location = None


    def download_progress_hook(self, d):
        # Progress hook for download updates
        if d['status'] == 'downloading':
            #percent = d.get('_percent_str', 'N/A')
            #print(f"Progress: {percent}")
            if self.download_status != 'downloading':
                self.download_status = 'downloading'
                self.status_manager.update_status_by_url(self.url, self.download_status, self.output_location)

        elif d['status'] == 'finished':
            print("✅ Download completed!")
            self.download_status = 'finished'
            self.status_manager.update_status_by_url(self.url, self.download_status, self.output_location)

    def execute_download(self, url, yt_opts):
        # Execute download
        try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download([url])

        except KeyboardInterrupt:
            print("\n⏹️ Download cancelled by user!")
            self.download_status = 'cancelled'
            self.status_manager.update_status_by_url(url, self.download_status, self.output_location)

        except yt_dlp.utils.DownloadError as e:
            print(f"Download error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url, self.download_status, self.output_location)

        except yt_dlp.utils.ExtractorError as e:
            print(f"Extractor error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url, self.download_status, self.output_location)

        except Exception as e:
            print(f"Unexpected error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url, self.download_status, self.output_location)
   
    def show_format_list(self, url: Optional[str] = None):
        # Show available formats for a video
        # Get URL from any source
        url = url or self.url or get_valid_url(allow_quit=True)
        
        if url is None:  # User chose exit
            return
        
        # Validate URL
        if not _is_valid_url_format(url):
            print("❌ Invalid URL format. URL must start with http:// or https://")
            return
        
        # Update self.url
        self.url = url        
        yt_opts = {
            'listformats': True,
            'skip_download': True
            }
        self.execute_download(url, yt_opts)
        return True

    def download_single_video(self, url: Optional[str] = None,
                              required_video_quality: Optional[str] = None):
        # Download a single video
        # Get input if not provided
        url = url or self.url or get_valid_url(allow_quit=True)
    
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL format. URL must start with http:// or https://")
            return False
        self.url = url

        # Set video quality
        if required_video_quality:
            self.required_video_quality = required_video_quality
        else:
            #self.required_video_quality = 'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best'
            #self.required_video_quality = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best'
            #self.required_video_quality = '298+140'
            self.required_video_quality = 'best'

        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # لو المستخدم ألغى الاختيار
            print("❌ No location selected!")
            return False
        # Setup download options
        yt_opts = {
            'outtmpl': f'$HOME/{self.output_location}/reels/%(title).100s.%(ext)s',
            'format': self.required_video_quality,
            'merge_output_format': 'mp4',
            'embed_metadata': True,
            'writeinfojson': True,
            'writethumbnail': True,
            'embedthumbnail': True, 
            'progress_hooks': [self.download_progress_hook],
            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'[|｜❙•\-–—]', ''),
                    
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer, 'title', r'\s+', ' ')
                ],
                'when': 'pre_process'
            }]
            }        
        self.execute_download(url, yt_opts)
        return True
