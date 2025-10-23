#!/usr/bin/env python3

from typing import Optional, Dict, Any, List

def _is_valid_url_format(url: str) -> bool:
    # Check if URL has valid format
    if not url:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    return True

def get_valid_url(url: Optional[str] = None,
                  allow_quit: bool = True) -> Optional[str]:
    # Get and validate URL from user or parameter
    # لو URL متمرر
    if url:
        if _is_valid_url_format(url):
            return url
        else:
            print("❌ Invalid URL format")
            return None
    # لو URL مش موجود - نطلبه
    while True:
        print("Enter URL" + (" (or 'q' to quit)" if allow_quit else "") + ":")
        url = input().strip()
        
        if allow_quit and url.lower() in ['q', 'quit', 'exit']:
            return None
        
        if not url:
            print("❌ URL cannot be empty")
            continue
        
        if not _is_valid_url_format(url):
            print("❌ Invalid URL format. Must start with http:// or https://")
            continue 
        return url
   
