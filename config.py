import os
# Define main path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Other paths
os.makedirs(DATA_DIR, exist_ok=True)
DATA_DIR = os.path.join(BASE_DIR, 'data')
FORMATS_FILE = os.path.join(DATA_DIR, 'formats.txt')
LOCATIONS_FILE = os.path.join(DATA_DIR, 'locations.txt')
HISTORY_FILE = os.path.join(DATA_DIR, 'download_history.json')
PENDING_URLS_FILE = os.path.join(DATA_DIR, 'pending_urls.txt')
