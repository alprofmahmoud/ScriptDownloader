from typing import Optional


def _is_valid_url_format(url: str) -> bool:
    # Check if URL has valid format
    if not url:
        return False
    if not url.startswith(('http://', 'https://')):
        return False
    return True


def get_valid_url(url: Optional[str] = None,
                  allow_quit: bool = True,
                  max_attempts: int = 3
                  ) -> Optional[str]:
    # Get and validate URL from user or parameter
    # If URL is passed
    if url:
        if _is_valid_url_format(url):
            return url
        else:
            print("❌ Invalid URL format")
            return None
    attempt = 0
    # If URL doesn't exist - ask for it
    while attempt < max_attempts:
        attempt += 1
        if max_attempts > 1:
            print(f"\n🔄 Attempt {attempt} of {max_attempts}")
        print("Enter URL" + (" (or 'q' to quit)" if allow_quit else "") + ":")
        url = input().strip()
        if allow_quit and url.lower() in ['q', 'quit', 'exit']:
            print("👋 Exiting...")
            exit()
        if not url:
            print("❌ URL cannot be empty")
            if attempt < max_attempts:
                print(f"❗{max_attempts - attempt} attempt(s) remaining")
            continue
        if not _is_valid_url_format(url):
            print("❌ Invalid URL format. Must start with http:// or https://")
            if attempt < max_attempts:
                print(f"❗{max_attempts - attempt} attempt(s) remaining")
            continue
        print("✅ Valid URL format")
        return url
    print("👋 Exiting...")
    exit()
