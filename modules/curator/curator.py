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

# Import Metaforge components
from metaforge.metadata_manager import Metaforge
from metaforge.schemas import ImageMetadataSchema
from metaforge.utils import export_metadata_to_json, export_metadata_to_yaml

# Additional imports for image metadata extraction
from PIL import Image
from PIL.ExifTags import TAGS

# Configuration
BASE_DIR = 'downloaded_images'
DEFAULT_SEARCH_TERMS = ['nature', 'city', 'animals', 'space', 'ocean']
DEFAULT_MAX_IMAGES_PER_TERM = 100

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
                logger.debug('Configuration loaded successfully.')
        else:
            logger.error(f'Configuration file {file_path} not found.')
            self.data = {}

config = Config()

def setup_logging():
    # Remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Use log directory from config or default to ./logs
    log_directory = config.data.get('log_directory', './logs')
    # Ensure log directory exists
    ensure_directory_exists(log_directory)

    # Logging configuration
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler for logging (keep at DEBUG level)
    log_file_path = os.path.join(log_directory, 'curator.log')
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

def ensure_directory_exists(path: str):
    try:
        os.makedirs(path, exist_ok=True)
        logger.debug(f'Directory ensured: {path}')
    except Exception as e:
        logger.error(f'Error creating directory {path}: {e}')
        raise

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
        logger.debug(f'Successfully downloaded image from {url} to {path}')
        return True
    except Exception as e:
        with METRICS_LOCK:
            METRICS['failed_requests'] += 1
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

def extract_file_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata from the image file using Pillow.
    """
    metadata = {}
    try:
        with Image.open(image_path) as img:
            info = img._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    metadata[decoded] = value
        logger.debug(f'Extracted file metadata from {image_path}: {metadata}')
    except Exception as e:
        logger.error(f"Error extracting file metadata from {image_path}: {e}")
    return metadata

def save_metadata(
    api: str,
    image_id: str,
    metadata: Dict[str, Any],
    folder: str,
    metaforge: Metaforge,
    extract_file_meta: bool = False
):
    """
    Save metadata to Metaforge.
    If extract_file_meta is True, extract metadata from the image file.
    Additionally, save a comprehensive metadata file in the module's directory.
    """
    image_path = os.path.join(folder, f"{metadata.get('filename', image_id)}")
    if extract_file_meta and os.path.exists(image_path):
        file_meta = extract_file_metadata(image_path)
        metadata['file_metadata'] = file_meta

    # Create ImageMetadataSchema instance
    image_metadata_schema = ImageMetadataSchema(
        image_id=image_id,
        source_api=api,
        download_info=metadata.get('download_info', {}),
        attribution=metadata.get('attribution', {}),
        additional_metadata=metadata.get('additional_metadata', {}),
        lineage=metadata.get('lineage', []),
        file_metadata=metadata.get('file_metadata', {})
    )

    # Add metadata to Metaforge (SQL Database)
    metaforge.add_image_metadata(image_metadata_schema)

    # Save comprehensive metadata file in the module's directory
    comprehensive_metadata_path = os.path.join(folder, f"{image_id}_metadata.json")
    try:
        with open(comprehensive_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(image_metadata_schema.dict(), f, indent=2)
        logger.debug(f'Comprehensive metadata saved at {comprehensive_metadata_path}')
    except Exception as e:
        logger.error(f"Error saving comprehensive metadata to {comprehensive_metadata_path}: {e}")

def download_image_and_save_metadata(
    image: Dict[str, Any],
    image_id: str,
    image_url: str,
    image_path: str,
    api_name: str,
    category_folder: str,
    metaforge: Metaforge,
    extract_file_meta: bool = False
) -> bool:
    success = download_image(image_url, image_path)
    if success:
        # Extract necessary attribution and license information
        attribution_info = extract_attribution_info(api_name, image)
        # Extract additional metadata
        additional_metadata = extract_additional_metadata(api_name, image)
        # Save metadata, optionally extracting file-based metadata
        save_metadata(
            api_name,
            image_id,
            {
                'download_info': {
                    'url': image_url,
                    'download_timestamp': datetime.utcnow().isoformat(),
                    'download_status': 'success'
                },
                'attribution': attribution_info,
                'additional_metadata': additional_metadata,
                'filename': os.path.basename(image_path)
            },
            category_folder,
            metaforge,
            extract_file_meta
        )
    return success

def extract_attribution_info(api_name: str, image: Dict[str, Any]) -> Dict[str, Any]:
    attribution = {}
    # Implement API-specific attribution extraction
    if api_name == 'pixabay':
        attribution = {
            'author': image.get('user'),
            'license': 'CC0',
            'source_url': image.get('pageURL')
        }
    elif api_name == 'unsplash':
        attribution = {
            'author': image.get('user', {}).get('name'),
            'license': 'Unsplash License',
            'source_url': image.get('links', {}).get('html')
        }
    elif api_name == 'pexels':
        attribution = {
            'author': image.get('photographer'),
            'license': 'Pexels License',
            'source_url': image.get('url')
        }
    elif api_name == 'flickr':
        attribution = {
            'author': image.get('owner', {}).get('username'),
            'license': image.get('license'),
            'source_url': image.get('link')
        }
    elif api_name == 'google_cse':
        attribution = {
            'author': image.get('displayLink'),
            'license': 'Google CSE License',
            'source_url': image.get('link')
        }
    # Add other APIs as needed
    return attribution

def extract_additional_metadata(api_name: str, image: Dict[str, Any]) -> Dict[str, Any]:
    additional = {}
    # Implement API-specific metadata extraction
    if api_name == 'pixabay':
        additional = {
            'tags': image.get('tags', '').split(', '),
            'resolution': f"{image.get('imageWidth')}x{image.get('imageHeight')}",
            'size': image.get('imageSize')
        }
    elif api_name == 'unsplash':
        additional = {
            'tags': [tag['title'] for tag in image.get('tags', [])],
            'resolution': f"{image.get('width')}x{image.get('height')}",
            'size': image.get('width') * image.get('height')  # Example metric
        }
    elif api_name == 'pexels':
        additional = {
            'tags': image.get('tags', []),
            'resolution': f"{image.get('width')}x{image.get('height')}",
            'size': image.get('width') * image.get('height')  # Example metric
        }
    elif api_name == 'flickr':
        additional = {
            'tags': image.get('tags', '').split(' '),
            'resolution': f"{image.get('width')}x{image.get('height')}",
            'size': image.get('size')  # Flickr API may provide size differently
        }
    elif api_name == 'google_cse':
        additional = {
            'tags': image.get('title', '').split(' '),
            'resolution': image.get('image', {}).get('height'),
            'size': image.get('image', {}).get('byteSize')
        }
    # Add other APIs as needed
    return additional

def download_image_batch(
    api_call_function: Callable,
    api_name: str,
    params: Dict[str, Any],
    headers: Optional[Dict[str, str]],
    file_prefix: str,
    image_selector: Callable[[Dict[str, Any]], List[Dict[str, Any]]],
    category_folder: str,
    metaforge: Metaforge,
    max_images_per_term: int,
    extract_file_meta: bool = False
) -> int:
    futures = []
    total_downloaded = 0
    start_time = time.time()
    page = params.get('page', 1)

    with ThreadPoolExecutor(max_workers=8) as executor:
        with tqdm(total=max_images_per_term, desc=f"{api_name.capitalize()} - {params.get('query') or params.get('q')}", unit='img', leave=False) as pbar:
            while total_downloaded < max_images_per_term:
                data = api_call_function(params['url'], params, headers)
                if not data:
                    break
                images = image_selector(data)
                if not images:
                    break

                for image in images:
                    if total_downloaded >= max_images_per_term:
                        break

                    # Generate a unique image ID if not present
                    image_id = str(image.get('id') or image.get('title') or hash(image.get('link')))
                    image_url = image.get('url_o') or image.get('largeImageURL') or image.get('urls', {}).get('full') or image.get('src', {}).get('original') or image.get('link')
                    if not image_url:
                        continue

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
                    future = executor.submit(
                        download_image_and_save_metadata,
                        image,
                        image_id,
                        image_url,
                        file_path,
                        api_name,
                        category_folder,
                        metaforge,
                        extract_file_meta
                    )
                    futures.append(future)
                    total_downloaded += 1
                    pbar.update(1)

                # Increment page number
                params['page'] = page = page + 1

                # Check if there are more pages (this logic can be enhanced based on API)
                if 'totalHits' in data and total_downloaded >= data['totalHits']:
                    logger.info(f"No more images available for term '{params.get('q') or params.get('query')}' from {api_name}")
                    break

    # Ensure all futures are completed
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            logger.error(f"Error processing image: {e}")

    with METRICS_LOCK:
        METRICS['total_images_downloaded'] += total_downloaded
        METRICS['images_per_category'][category_folder] += total_downloaded
        METRICS['api_times'][api_name] += time.time() - start_time

    return total_downloaded

def download_from_pixabay(
    term: str,
    metaforge: Metaforge,
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    extract_file_meta: bool = False
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

    if not check_images_exist(general_api_call, url, params, None):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def pixabay_image_selector(data):
        return data.get('hits', [])

    total_downloaded = download_image_batch(
        general_api_call,
        api_name,
        params,
        None,
        'pixabay',
        pixabay_image_selector,
        category_folder,
        metaforge,
        max_images_per_term,
        extract_file_meta
    )

    return total_downloaded

def download_from_unsplash(
    term: str,
    metaforge: Metaforge,
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    extract_file_meta: bool = False
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
        general_api_call,
        api_name,
        params,
        headers,
        'unsplash',
        unsplash_image_selector,
        category_folder,
        metaforge,
        max_images_per_term,
        extract_file_meta
    )

    return total_downloaded

def download_from_pexels(
    term: str,
    metaforge: Metaforge,
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    extract_file_meta: bool = False
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
        general_api_call,
        api_name,
        params,
        headers,
        'pexels',
        pexels_image_selector,
        category_folder,
        metaforge,
        max_images_per_term,
        extract_file_meta
    )

    return total_downloaded

def download_from_flickr(
    term: str,
    metaforge: Metaforge,
    starting_page: int = 1,
    api_key: Optional[str] = None,
    max_images_per_term: int = 100,
    extract_file_meta: bool = False
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

    if not check_images_exist(general_api_call, url, params, None):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def flickr_image_selector(data):
        return data.get('photos', {}).get('photo', [])

    total_downloaded = download_image_batch(
        general_api_call,
        api_name,
        params,
        None,
        'flickr',
        flickr_image_selector,
        category_folder,
        metaforge,
        max_images_per_term,
        extract_file_meta
    )

    return total_downloaded

def download_from_google_cse(
    term: str,
    metaforge: Metaforge,
    starting_page: int = 1,
    api_key: Optional[str] = None,
    search_engine_id: Optional[str] = None,
    max_images_per_term: int = 100,
    extract_file_meta: bool = False
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

    if not check_images_exist(general_api_call, url, params, None):
        logger.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def google_cse_image_selector(data):
        return data.get('items', [])

    total_downloaded = download_image_batch(
        general_api_call,
        api_name,
        params,
        None,
        'google_cse',
        google_cse_image_selector,
        category_folder,
        metaforge,
        max_images_per_term,
        extract_file_meta
    )

    return total_downloaded

# Define a mapping for API name-to-function
API_FUNCTIONS = {
    'pixabay': download_from_pixabay,
    'unsplash': download_from_unsplash,
    'pexels': download_from_pexels,
    'flickr': download_from_flickr,
    'google_cse': download_from_google_cse
}

def general_api_call(url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    with METRICS_LOCK:
        METRICS['total_requests_made'] += 1
    logger.debug(f'Calling API: {url} with params: {params}')
    session = requests.Session()

    try:
        response = session.get(url, params=params, headers=headers, timeout=10)
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

def download_images(
    api_function_mapping: Dict[str, Callable],
    search_terms: List[str],
    metaforge: Metaforge,
    max_images_per_term: int,
    extract_file_meta: bool = True  # Extraction is on by default
):
    for term in search_terms:
        for api_name, api_func in api_function_mapping.items():
            logger.info(f'Starting download from {api_name} for term: "{term}"')

            # Retrieve API key from config
            api_keys = config.data.get('api_keys', {})
            api_key_data = api_keys.get(api_name, {})
            api_key_value = api_key_data.get('key')

            if not api_key_value:
                logger.warning(f"No API key found for {api_name}. Skipping.")
                continue

            # API specific arguments
            api_args = {
                'term': term,
                'metaforge': metaforge,
                'starting_page': 1,
                'api_key': api_key_value,
                'max_images_per_term': max_images_per_term,
                'extract_file_meta': extract_file_meta
            }

            if api_name == 'google_cse':
                api_args['search_engine_id'] = api_key_data.get("search_engine_id")
                if not api_args['search_engine_id']:
                    logger.warning("No search_engine_id provided for Google CSE. Skipping.")
                    continue

            total_downloaded = api_func(**api_args)

            logger.info(f'Total images downloaded from {api_name} for term "{term}": {total_downloaded}')

def send_email_notification(email_address: str, subject: str, body: str):
    email_settings = config.data.get('email_settings', {})
    if not email_settings:
        logger.error('Email settings not configured.')
        return

    msg = EmailMessage()
    msg.set_content(body, subtype='html')  # Use HTML for better formatting
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

def clean_up_partial_files(base_dir: str):
    logger.info('Cleaning up any partial files...')
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.part'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    logger.debug(f'Removed partial file: {file_path}')
                except Exception as e:
                    logger.error(f'Error removing partial file {file_path}: {e}')

def main():
    parser = argparse.ArgumentParser(description='Download images from APIs.')
    parser.add_argument('--config', type=str, help='Path to the configuration file.')
    parser.add_argument('--email', '-e', action='store_true', help='Enable email notifications.')
    args = parser.parse_args()

    config_path = args.config or 'config/config.yaml'
    config.load(config_path)

    # Setup logging after loading config
    setup_logging()

    ensure_directory_exists(BASE_DIR)

    # Initialize Metaforge with database URL from config
    metaforge = Metaforge(db_url=config.data.get('database', {}).get('url', 'sqlite:///metaforge.db'))

    # Clean up any partial files from previous runs
    clean_up_partial_files(BASE_DIR)

    # Load search terms and max images
    search_terms = config.data.get('search_terms', DEFAULT_SEARCH_TERMS)
    max_images_per_term = config.data.get('max_images_per_term', DEFAULT_MAX_IMAGES_PER_TERM)
    extract_file_meta = config.data.get('extract_file_meta', True)  # Extraction is on by default

    # Define API functions mapping
    API_FUNCTIONS = {
        'pixabay': download_from_pixabay,
        'unsplash': download_from_unsplash,
        'pexels': download_from_pexels,
        'flickr': download_from_flickr,
        'google_cse': download_from_google_cse
    }

    download_images(API_FUNCTIONS, search_terms, metaforge, max_images_per_term, extract_file_meta)

    # Export metadata
    export_dir = config.data.get('metadata_export_dir', 'metaforge/exports/curator')
    ensure_directory_exists(export_dir)
    metaforge.export_metadata(['json', 'yaml'], export_dir=export_dir)

    # Print summary
    logger.info("\nDownload Summary:")
    logger.info(f"Total images downloaded: {METRICS['total_images_downloaded']}")
    logger.info("Images per category:")
    for category, count in METRICS['images_per_category'].items():
        logger.info(f"  {category}: {count} images")

    if METRICS['failed_requests'] > 0:
        logger.warning(f"Failed requests: {METRICS['failed_requests']}")

    # Send email notification if enabled
    if args.email and config.data.get('email_settings', {}).get('enabled', False):
        subject = 'Curator - Image Download Report'
        body = f"""
        <h2>Curator - Image Download Report</h2>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total images downloaded:</strong> {METRICS['total_images_downloaded']}</p>
        <p><strong>Images per category:</strong></p>
        <ul>
        """
        for category, count in METRICS['images_per_category'].items():
            body += f"<li>{category}: {count} images</li>"
        body += "</ul>"
        body += f"""
        <p><strong>Total requests made:</strong> {METRICS['total_requests_made']}</p>
        <p><strong>Successful requests:</strong> {METRICS['successful_requests']}</p>
        <p><strong>Failed requests:</strong> {METRICS['failed_requests']}</p>
        <p><strong>API time spent:</strong></p>
        <ul>
        """
        for api, duration in METRICS['api_times'].items():
            body += f"<li>{api}: {duration:.2f} seconds</li>"
        body += "</ul>"
        body += f"""
        <p><strong>API retries:</strong></p>
        <ul>
        """
        for api, retries in METRICS['api_retries'].items():
            body += f"<li>{api}: {retries} retries</li>"
        body += "</ul>"
        send_email_notification(config.data['email_settings']['to_email'], subject, body)

    # Close Metaforge connection
    metaforge.close_connection()

if __name__ == '__main__':
    main()
