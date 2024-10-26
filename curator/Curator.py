import os
import json
import logging
import argparse
import requests
import yaml
from collections import defaultdict, Counter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from retry import retry
import smtplib
from email.message import EmailMessage
import threading
from typing import Any, Callable, Dict, List, Optional, Union
import time
from urllib.parse import urlparse  # Added import for URL parsing

# Configuration
MASTER_ATTRIBUTE_FILE = 'master_metadata.json'
GLOBAL_METADATA_FILE = 'global_metadata.json'
BASE_DIR = 'downloaded_images'
DEFAULT_SEARCH_TERMS = ['nature', 'city', 'animals', 'space', 'ocean']

# Initialize logger without handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Metrics dictionary (thread-safe)
METRICS = {
    'total_images_downloaded': 0,
    'images_per_category': Counter(),
    'total_requests_made': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'api_times': defaultdict(float),
    'api_retries': Counter()
}
METRICS_LOCK = threading.Lock()

# Global configuration variable
class Config:
    def __init__(self):
        self.data = {}

    def load(self, file_path: str):
        logger.debug(f'Loading configuration from {file_path}')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.data = yaml.safe_load(file)
        else:
            logger.error(f'Configuration file {file_path} not found.')
            self.data = {}

config = Config()

def setup_logging():
    # Remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Use log directory from config or default to current directory
    log_directory = config.data.get('log_directory', '.')
    # Ensure log directory exists
    ensure_directory_exists(log_directory)

    # Logging configuration
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler for logging (keep at DEBUG level)
    log_file_path = os.path.join(log_directory, 'image_downloader.log')
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for logging (set to INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Set to INFO to reduce terminal output
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_current_date() -> str:
    return datetime.now().strftime('%Y%m%d')

def get_master_folder(api_name: str) -> str:
    return os.path.join(BASE_DIR, f'{api_name}_{get_current_date()}')

def get_category_folder(api: str, term: str) -> str:
    return os.path.join(get_master_folder(api), term)

def load_master_attributes(api: str) -> Dict[str, Any]:
    file_path = os.path.join(get_master_folder(api), MASTER_ATTRIBUTE_FILE)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_master_attributes(api: str, master_attributes: Dict[str, Any]):
    file_path = os.path.join(get_master_folder(api), MASTER_ATTRIBUTE_FILE)
    ensure_directory_exists(get_master_folder(api))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(master_attributes, f, indent=2)

def load_global_metadata() -> Dict[str, Any]:
    file_path = os.path.join(BASE_DIR, GLOBAL_METADATA_FILE)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_global_metadata(global_metadata: Dict[str, Any]):
    file_path = os.path.join(BASE_DIR, GLOBAL_METADATA_FILE)
    ensure_directory_exists(BASE_DIR)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(global_metadata, f, indent=2)

@retry(tries=5, delay=2, backoff=2)
def download_image(url: str, path: str) -> bool:
    with METRICS_LOCK:
        METRICS['total_requests_made'] += 1
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        with METRICS_LOCK:
            METRICS['successful_requests'] += 1
        return True
    except Exception as e:
        with METRICS_LOCK:
            METRICS['failed_requests'] += 1
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

def save_metadata(api: str, image_id: str, metadata: Dict[str, Any], folder: str, master_attributes: Dict[str, Any], global_metadata: Dict[str, Any]):
    metadata_path = os.path.join(folder, "metadata.json")
    api_metadata = {
        f"{api}_{image_id}": {
            'api': api,
            'id': image_id,
            'metadata': metadata
        }
    }

    # Save per-category metadata
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            existing_metadata = json.load(f)
    else:
        existing_metadata = {}

    existing_metadata.update(api_metadata)

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(existing_metadata, f, indent=2)

    # Update master attributes
    master_attributes.update(api_metadata)

    # Update global metadata
    global_metadata.update(api_metadata)

# Custom SimpleRateLimiter Class
class SimpleRateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.lock = threading.Lock()
        self.calls = []
        self.max_calls = max_calls
        self.period = period

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self.lock:
                current_time = time.time()
                # Remove calls that are outside the rate limit period
                self.calls = [call for call in self.calls if call > current_time - self.period]
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.calls[0] + self.period - current_time
                    if sleep_time > 0:
                        logger.debug(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds.")
                        time.sleep(sleep_time)
                self.calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper

# Updated rate_limit_decorator Function
def rate_limit_decorator(calls: Optional[int], period: Optional[int]) -> Callable:
    logger.debug(f'Applying rate limit: {calls} calls per {period} seconds')
    if calls is None or period is None:
        def decorator(func):
            return func
        return decorator
    else:
        return SimpleRateLimiter(calls, period)

def ensure_directory_exists(path: str):
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f'Directory ensured: {path}')
    except Exception as e:
        logger.error(f'Error creating directory {path}: {e}')
        raise

def general_api_call(url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, rate_limit_info: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
    with METRICS_LOCK:
        METRICS['total_requests_made'] += 1
    logger.debug(f'Calling API: {url} with params: {params}')
    session = requests.Session()

    # Handle null rate limits
    calls = rate_limit_info.get('calls') if rate_limit_info else None
    period = rate_limit_info.get('period') if rate_limit_info else None

    @rate_limit_decorator(calls, period)
    def rate_limited_get(url, params=None, headers=None):
        return session.get(url, params=params, headers=headers, timeout=10)

    try:
        response = rate_limited_get(url, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.debug(f'API response received from {url}')
        with METRICS_LOCK:
            METRICS['successful_requests'] += 1
        return result
    except Exception as e:
        with METRICS_LOCK:
            METRICS['failed_requests'] += 1
        logger.error(f"Error in API request to {url}: {str(e)}")
        return None
    finally:
        session.close()

def check_images_exist(api_call_function: Callable, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> bool:
    try:
        data = api_call_function(url, params, headers)
        logger.debug(f'Checking if images exist in data from {url}')
        if not data:
            return False
        if 'hits' in data:
            return bool(data['hits'])
        elif 'results' in data:
            return bool(data['results'])
        elif 'photos' in data and 'photo' in data['photos']:
            return bool(data['photos']['photo'])
        elif 'items' in data:
            return bool(data['items'])
        elif 'photos' in data:
            return bool(data['photos'])
        return False
    except Exception as e:
        logger.error(f"Error in API request while checking images exist: {str(e)}")
        return False

def is_duplicate_image(image_key: str, global_metadata: Dict[str, Any]) -> bool:
    return image_key in global_metadata

def download_image_batch(
    api_call_function: Callable,
    api_name: str,
    params: Dict[str, Any],
    headers: Optional[Dict[str, str]],
    file_prefix: str,
    image_selector: Callable[[Dict[str, Any]], List[Dict[str, Any]]],
    category_folder: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    max_images_per_term: int,
    rate_limits: Optional[Dict[str, int]]
) -> int:
    futures = []
    total_downloaded = 0
    start_time = time.time()
    page = params.get('page', 1)

    with ThreadPoolExecutor(max_workers=8) as executor:
        with tqdm(total=max_images_per_term, desc=f"{api_name.capitalize()} - {params.get('query') or params.get('q')}", unit='img', leave=False) as pbar:
            while total_downloaded < max_images_per_term:
                data = api_call_function(params['url'], params, headers, rate_limits)
                if not data:
                    break
                images = image_selector(data)
                if not images:
                    break

                for image in images:
                    if total_downloaded >= max_images_per_term:
                        break

                    image_id = str(image.get('id') or image.get('title') or hash(image.get('link')))
                    image_key = f"{api_name}_{image_id}"

                    if is_duplicate_image(image_key, global_metadata):
                        logger.debug(f"Duplicate image found in global metadata, skipping: {image_id}")
                        continue

                    image_url = image.get('url_o') or image.get('largeImageURL') or image.get('urls', {}).get('full') or image.get('src', {}).get('original') or image.get('link')
                    if not image_url:
                        continue

                    ensure_directory_exists(category_folder)

                    # Extract the file extension from the URL path
                    parsed_url = urlparse(image_url)
                    image_path = parsed_url.path
                    image_extension = os.path.splitext(image_path)[1]  # Correctly extract the extension

                    # Validate the extension
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                    if image_extension.lower() not in valid_extensions:
                        image_extension = '.jpg'  # Default to .jpg if invalid

                    # Generate the file name and path
                    file_name = f"{file_prefix}_{image_id}{image_extension}"
                    file_path = os.path.join(category_folder, file_name)
                    future = executor.submit(download_image, image_url, file_path)
                    futures.append(future)
                    save_metadata(api_name, image_id, image, category_folder, master_attributes, global_metadata)
                    total_downloaded += 1
                    pbar.update(1)

                # Increment page number
                params['page'] = page = page + 1

                # Check if there are more pages
                if 'totalHits' in data and total_downloaded >= data['totalHits']:
                    logger.info(f"No more images available for term '{params.get('q') or params.get('query')}' from {api_name}")
                    break

        # Ensure all futures are completed
        for future in as_completed(futures):
            future.result()

    with METRICS_LOCK:
        METRICS['total_images_downloaded'] += total_downloaded
        METRICS['images_per_category'][category_folder] += total_downloaded
        METRICS['api_times'][api_name] += time.time() - start_time

    return total_downloaded

def download_from_pixabay(
    term: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    rate_limits: Optional[Dict[str, int]] = None
) -> int:
    api_name = 'pixabay'
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": term,
        "safesearch": "true",
        "image_type": "photo",
        "per_page": 200,
        "page": starting_page,
        "url": url
    }

    if not check_images_exist(general_api_call, url, params):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def pixabay_image_selector(data):
        return data.get('hits', [])

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, None, 'pixabay', pixabay_image_selector,
        category_folder, master_attributes, global_metadata, max_images_per_term, rate_limits
    )

    return total_downloaded

def download_from_unsplash(
    term: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    rate_limits: Optional[Dict[str, int]] = None
) -> int:
    api_name = 'unsplash'
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {
        "query": term,
        "per_page": 30,
        "page": starting_page,
        "url": url
    }

    if not check_images_exist(general_api_call, url, params, headers):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def unsplash_image_selector(data):
        return data.get('results', [])

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, headers, 'unsplash', unsplash_image_selector,
        category_folder, master_attributes, global_metadata, max_images_per_term, rate_limits
    )

    return total_downloaded

def download_from_pexels(
    term: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    rate_limits: Optional[Dict[str, int]] = None
) -> int:
    logger.debug(f'Starting download from Pexels with term: {term}')
    api_name = 'pexels'
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {
        "query": term,
        "per_page": 80,
        "page": starting_page,
        "url": url
    }

    if not check_images_exist(general_api_call, url, params, headers):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)
    logger.debug(f'Category folder for Pexels: {category_folder}')

    def pexels_image_selector(data):
        return data.get('photos', [])

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, headers, 'pexels', pexels_image_selector,
        category_folder, master_attributes, global_metadata, max_images_per_term, rate_limits
    )

    return total_downloaded

def download_from_flickr(
    term: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    rate_limits: Optional[Dict[str, int]] = None
) -> int:
    api_name = 'flickr'
    url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
        "text": term,
        "format": "json",
        "nojsoncallback": 1,
        "extras": "url_o",
        "per_page": 100,
        "page": starting_page,
        "url": url
    }

    if not check_images_exist(general_api_call, url, params):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def flickr_image_selector(data):
        return data.get('photos', {}).get('photo', [])

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, None, 'flickr', flickr_image_selector,
        category_folder, master_attributes, global_metadata, max_images_per_term, rate_limits
    )

    return total_downloaded

def download_from_google_cse(
    term: str,
    master_attributes: Dict[str, Any],
    global_metadata: Dict[str, Any],
    starting_page: int = 1,
    api_key: Optional[str] = None,
    search_engine_id: Optional[str] = None,
    max_images_per_term: int = 100,
    rate_limits: Optional[Dict[str, int]] = None
) -> int:
    api_name = 'google_cse'
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": term,
        "searchType": "image",
        "num": 10,
        "start": (starting_page - 1) * 10 + 1,
        "url": url
    }

    if not check_images_exist(general_api_call, url, params):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def google_cse_image_selector(data):
        return data.get('items', [])

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, None, 'google_cse', google_cse_image_selector,
        category_folder, master_attributes, global_metadata, max_images_per_term, rate_limits
    )

    return total_downloaded

# Define a mapping for API name-to-function
API_FUNCTIONS = {
    'pixabay': {'func': download_from_pixabay, 'name': 'pixabay'},
    'unsplash': {'func': download_from_unsplash, 'name': 'unsplash'},
    'pexels': {'func': download_from_pexels, 'name': 'pexels'},
    'flickr': {'func': download_from_flickr, 'name': 'flickr'},
    'google_cse': {'func': download_from_google_cse, 'name': 'google_cse'}
}

def download_images(api_function_mapping: Dict[str, Dict[str, Any]], search_terms: List[str], global_metadata: Dict[str, Any], max_images_per_term: int):
    for term in search_terms:
        for api_key, api_info in api_function_mapping.items():
            api_func = api_info['func']
            api_name = api_info['name']

            logger.info(f'Starting download from {api_name} for term: {term}')

            # Retrieve API key from config
            api_keys = config.data.get('api_keys', {})
            api_key_data = api_keys.get(api_name, {})
            api_key_value = api_key_data.get('key')

            if not api_key_value:
                logger.warning(f"No API key found for {api_name}. Skipping.")
                continue

            # Load master attributes for this API
            master_attributes = load_master_attributes(api_name)

            # API specific arguments
            api_args = {
                'term': term,
                'master_attributes': master_attributes,
                'global_metadata': global_metadata,
                'starting_page': 1,
                'api_key': api_key_value,
                'max_images_per_term': max_images_per_term,
                'rate_limits': config.data.get('rate_limits', {}).get(api_name),
            }

            if api_name == 'google_cse':
                api_args['search_engine_id'] = api_key_data.get("search_engine_id")
                if not api_args['search_engine_id']:
                    logger.warning("No search_engine_id provided for Google CSE. Skipping.")
                    continue

            total_downloaded = api_func(**api_args)

            # Save master attributes after downloading
            save_master_attributes(api_name, master_attributes)

            logger.info(f'Total images downloaded from {api_name} for term "{term}": {total_downloaded}')

def send_email_notification(email_address: str, subject: str, body: str):
    email_settings = config.data.get('email_settings', {})
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_settings.get('from_email')
    msg['To'] = email_address

    try:
        with smtplib.SMTP(email_settings.get('smtp_server'), email_settings.get('smtp_port')) as s:
            s.starttls()
            s.login(email_settings.get('smtp_login'), email_settings.get('smtp_password'))
            s.send_message(msg)
            logger.info('Email notification sent successfully.')
    except Exception as e:
        logger.error(f'Failed to send email notification: {e}')

def main():
    parser = argparse.ArgumentParser(description='Download images from APIs.')
    parser.add_argument('--config', type=str, help='Path to the configuration file.')
    parser.add_argument('--email', '-e', action='store_true', help='Enable email notifications.')

    args = parser.parse_args()

    config_path = args.config or 'config.yaml'
    config.load(config_path)

    # Setup logging after loading config
    setup_logging()

    ensure_directory_exists(BASE_DIR)

    # Load global metadata
    global_metadata = load_global_metadata()

    search_terms = config.data.get('search_terms', DEFAULT_SEARCH_TERMS)
    max_images_per_term = config.data.get('max_images_per_term', 1)

    download_images(API_FUNCTIONS, search_terms, global_metadata, max_images_per_term)

    # Save global metadata
    save_global_metadata(global_metadata)

    # Print summary
    logger.info("\nDownload Summary:")
    logger.info(f"Total images downloaded: {METRICS['total_images_downloaded']}")
    logger.info("Images per category:")
    for category, count in METRICS['images_per_category'].items():
        logger.info(f"  {category}: {count} images")

    if METRICS['failed_requests'] > 0:
        logger.warning(f"Failed requests: {METRICS['failed_requests']}")

    if args.email:
        subject = 'Image Download Report'
        body = f"""
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Total images downloaded: {METRICS['total_images_downloaded']}
        Images per category: {json.dumps({k: v for k, v in METRICS['images_per_category'].items()}, indent=2)}
        Total requests made: {METRICS['total_requests_made']}
        Successful requests: {METRICS['successful_requests']}
        Failed requests: {METRICS['failed_requests']}
        API time spent: {json.dumps({k: v for k, v in METRICS['api_times'].items()}, indent=2)}
        API retries: {json.dumps({k: v for k, v in METRICS['api_retries'].items()}, indent=2)}
        """
        send_email_notification(config.data['email_settings']['to_email'], subject, body)

if __name__ == '__main__':
    main()
