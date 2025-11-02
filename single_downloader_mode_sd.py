#!/usr/bin/env python3

import yt_dlp
import re
from typing import Optional
from utils.validators import _is_valid_url_format, get_valid_url
from utils.status_manager import StatusManager
from utils.select_output_location import select_output_location
from utils.select_format import select_format


class SingleDownloader:
    def __init__(self, url=None):
        self.url = url
        self.required_video_quality = None
        self.status_manager = StatusManager('./download_history_file.json')
        self.download_status = None
        self.percent_str = '0 %'
        self.output_location = None
        self.format_id = None
        self.video_title = None
        self.total_playlist_videos = None

    def _extract_info(self, d):
        """Extract common info from download dict"""
        percent_str_raw = d.get('_percent_str', '0%')
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str_raw).strip()
        filename = d.get('filename', 'N/A')
        info_dict = d.get('info_dict') or {}
        return {
            'percent_str': percent_str,
            'filename': filename,
            'info_dict': info_dict,
            'playlist_title': info_dict.get('playlist_title'),
            'playlist_index': info_dict.get('playlist_index'),
            'playlist_count': info_dict.get('n_entries'),
            'format_id': info_dict.get('format_id', 'N/A'),
            'video_title': info_dict.get('title', 'N/A')
        }

    def download_progress_hook(self, d):
        # Progress hook for download updates
        if d['status'] == 'downloading':
            info = self._extract_info(d)
            self.percent_str = info['percent_str']
            filename = info['filename']
            info_dict = info['info_dict']
            playlist_title = info['playlist_title']
            playlist_index = info['playlist_index']
            playlist_count = info['playlist_count']
            if self.download_status != 'downloading':
                self.download_status = 'downloading'
                self.video_title = info_dict.get('title', 'N/A')
                self.format_id = info_dict.get('format_id', 'N/A')

            # Update status
            if playlist_index is None:
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.output_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title
                    )

            else:
                video_url = info_dict.get('webpage_url') or \
                        info_dict.get('url')
                self.status_manager.update_status_by_url_playlist(
                    playlist_url=self.url,
                    video_url=video_url,
                    new_status=self.download_status,
                    output_location=self.output_location,
                    percent_str=self.percent_str,
                    format_id=self.format_id,
                    video_title=self.video_title,
                    extra_info={
                            'playlist_title': playlist_title,
                            'filename': filename,
                            'playlist_index': playlist_index,
                            'playlist_count': playlist_count,
                            'total_playlis_videos': self.total_playlist_videos
                                }
                    )

        elif d['status'] == 'finished':
            print(" ✅ Download completed!")
            self.download_status = 'finished'
            info = self._extract_info(d)
            self.percent_str = info['percent_str']
            filename = info['filename']
            info_dict = info['info_dict']
            playlist_title = info['playlist_title']
            playlist_index = info['playlist_index']
            playlist_count = info['playlist_count']
            self.format_id = info_dict.get('format_id', 'N/A')
            self.video_title = info_dict.get('title', 'N/A')
            if playlist_index is None:
                # Update status
                self.status_manager.update_status_by_url(
                    self.url,
                    self.download_status,
                    self.output_location,
                    self.percent_str,
                    self.format_id,
                    self.video_title
                    )
            else:
                video_url = info_dict.get('webpage_url') or \
                        info_dict.get('url')
                self.status_manager.update_status_by_url_playlist(
                    playlist_url=self.url,
                    video_url=video_url,
                    new_status=self.download_status,
                    output_location=self.output_location,
                    percent_str=self.percent_str,
                    format_id=self.format_id,
                    video_title=self.video_title,
                    extra_info={
                            'playlist_title': playlist_title,
                            'filename': filename,
                            'playlist_index': playlist_index,
                            'playlist_count': playlist_count,
                            'total_playlist_videos': self.total_playlist_videos
                                }
                    )

    def execute_download(self, url, yt_opts, output_location=None):
        # Execute download
        self.url = url
        if output_location is not None:
            self.output_location = output_location
        try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download([url])

        except KeyboardInterrupt:
            print("\n⏹️ Download cancelled by user!")
            self.download_status = 'cancelled'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.output_location)

        except yt_dlp.utils.DownloadError as e:
            print(f"Download error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.output_location)

        except yt_dlp.utils.ExtractorError as e:
            print(f"Extractor error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.output_location)

        except Exception as e:
            print(f"Unexpected error: {e}")
            self.download_status = 'error'
            self.status_manager.update_status_by_url(url,
                                                     self.download_status,
                                                     self.output_location)

    def show_format_list(self, url: Optional[str] = None):
        # Show available formats for a video
        # Get URL from any source
        url = url or get_valid_url(allow_quit=True)
        if url is None:  # User chose exit
            return
        # Validate URL
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return
        # Update self.url
        self.url = None
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
        url = url or get_valid_url(allow_quit=True)
        if url is None:
            return
        if not _is_valid_url_format(url):
            print("❌ Invalid URL. Must start with http:// or https://")
            return False
        self.url = None

        # Set video quality
        # if required_video_quality is None:
        self.required_video_quality = select_format()
        """
        # else:
            # self.required_video_quality =
             'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best'
            # self.required_video_quality =
            'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best'
            #self.required_video_quality = '298+140'
            #self.required_video_quality = 'sd'
        """
        # Select output location
        self.output_location = select_output_location()
        if self.output_location is None:  # لو المستخدم ألغى الاختيار
            print("❌ No location selected!")
            return False
        # Setup download options
        yt_opts = {
            'outtmpl': (
                f'$HOME/{self.output_location}'
                f'/%(title).100s.%(ext)s'
                ),
            'format': self.required_video_quality,
            'merge_output_format': 'mp4',
            'embed_metadata': True,
            'progress_hooks': [self.download_progress_hook],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                    AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/120.0.0.0 Safari/537.36',
            'postprocessors': [{
                'key': 'MetadataParser',
                'actions': [
                    # First: Delete the specified characters
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'[|｜❙•\-–—]', ''),
                    # Second: Clean up extra spaces
                    (yt_dlp.postprocessor.MetadataParserPP.replacer,
                     'title', r'\s+', ' ')
                ],
                'when': 'pre_process'
            }]
            }
        self.execute_download(url, yt_opts)
        return True
