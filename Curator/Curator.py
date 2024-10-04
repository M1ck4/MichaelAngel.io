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
from ratelimit import limits, sleep_and_retry
from retry import retry
import smtplib
from email.message import EmailMessage
import time

# Configuration
MASTER_ATTRIBUTE_FILE = 'master_metadata.json'
BASE_DIR = 'downloaded_images'
DEFAULT_SEARCH_TERMS = ['nature', 'city', 'animals', 'space', 'ocean']

# Logging configuration
logging.basicConfig(filename='image_downloader.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Metrics dictionary
METRICS = {
    'total_images_downloaded': 0,
    'images_per_category': Counter(),
    'total_requests_made': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'api_times': defaultdict(float),
    'api_retries': Counter()
}

# Global configuration variable
config = {}


def load_config(file_path):
    logging.debug(f'Loading configuration from {file_path}')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    else:
        logging.error(f'Configuration file {file_path} not found.')
        return {}


def get_current_date():
    return datetime.now().strftime('%Y%m%d')


def get_master_folder(api_name):
    return os.path.join(BASE_DIR, f'{api_name}_{get_current_date()}')


def get_category_folder(api, term):
    return os.path.join(get_master_folder(api), term)


def load_master_attributes(api):
    file_path = os.path.join(get_master_folder(api), MASTER_ATTRIBUTE_FILE)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}


def save_master_attributes(api, master_attributes):
    file_path = os.path.join(get_master_folder(api), MASTER_ATTRIBUTE_FILE)
    ensure_directory_exists(get_master_folder(api))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(master_attributes, f, indent=2)


@retry(tries=5, delay=2, backoff=2)
def download_image(url, path):
    METRICS['total_requests_made'] += 1
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        METRICS['successful_requests'] += 1
        return True
    except Exception as e:
        METRICS['failed_requests'] += 1
        logging.error(f"Error downloading {url}: {str(e)}")
        return False


def save_metadata(api, image_id, metadata, folder, master_attributes):
    metadata_path = os.path.join(folder, "metadata.json")
    api_metadata = {
        f"{api}_{image_id}": {
            'api': api,
            'id': image_id,
            'metadata': metadata
        }
    }

    with open(metadata_path, 'a', encoding='utf-8') as f:
        json.dump(api_metadata, f, indent=2)

    master_attributes[f"{api}_{image_id}"] = api_metadata[f"{api}_{image_id}"]


def rate_limit_decorator(calls, period):
    logging.debug(f'Applying rate limit: {calls} calls per {period} seconds')
    if calls is None or period is None:
        def no_rate_limit_decorator(func):
            return func

        return no_rate_limit_decorator
    else:
        return lambda func: sleep_and_retry(limits(calls=calls, period=period)(func))


def ensure_directory_exists(path):
    if not os.path.exists(path):
        logging.debug(f'Creating directory: {path}')
        os.makedirs(path)


def general_api_call(url, params, headers=None, rate_limit_info=None):
    METRICS['total_requests_made'] += 1
    logging.debug(f'Calling API: {url} with params: {params}')
    if rate_limit_info and rate_limit_info.get('calls') is not None and rate_limit_info.get('period') is not None:
        rate_limited_call = rate_limit_decorator(rate_limit_info['calls'], rate_limit_info['period'])(requests.get)
    else:
        rate_limited_call = requests.get

    try:
        response = rate_limited_call(url, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        logging.debug(f'API response: {result}')
        METRICS['successful_requests'] += 1
        return result
    except Exception as e:
        METRICS['failed_requests'] += 1
        logging.error(f"Error in API request to {url}: {str(e)}")
        return None


def check_images_exist(api_call_function, url, params, headers=None):
    try:
        data = api_call_function(url, params, headers)
        logging.debug(f'Checking if images exist in data: {data}')
        if 'hits' in data:
            return bool(data['hits'])
        elif 'results' in data:
            return bool(data['results'])
        elif 'photos' in data and 'photo' in data['photos']:
            return bool(data['photos']['photo'])
        elif 'items' in data:
            return bool(data['items'])
        return False
    except Exception as e:
        logging.error(f"Error in API request while checking images exist: {str(e)}")
        return False


def is_duplicate_image(image_id, master_attributes):
    return image_id in master_attributes


def download_image_batch(api_call_function, api_name, params, headers, file_prefix, image_selector,
                         category_folder, master_attributes, max_images_per_term, rate_limits):
    futures = []
    total_downloaded = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        with tqdm(total=max_images_per_term, desc=f"Downloading from {api_name}") as pbar:
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

                    image_id = image['id']
                    if is_duplicate_image(image_id, master_attributes):
                        logging.info(f"Duplicate image found, skipping: {image_id}")
                        continue

                    image_url = image.get('url_o') or image.get('largeImageURL') or image.get('urls', {}).get(
                        'raw') or image.get('src', {}).get('original')
                    if not image_url:
                        continue

                    ensure_directory_exists(category_folder)

                    file_name = f"{file_prefix}_{image_id}.jpg"
                    file_path = os.path.join(category_folder, file_name)
                    futures.append(executor.submit(download_image, image_url, file_path))
                    save_metadata(api_name, image_id, image, category_folder, master_attributes)
                    total_downloaded += 1
                    pbar.update(1)

                params['page'] += 1

        for future in as_completed(futures):
            future.result()

    METRICS['total_images_downloaded'] += total_downloaded
    METRICS['images_per_category'][category_folder] += total_downloaded
    METRICS['api_times'][api_name] += time.time() - start_time

    return total_downloaded


def download_from_pixabay(term, master_attributes, starting_page=1, api_key=None, max_images_per_term=100,
                          rate_limits=None):
    api_name = 'pixabay'
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": term,
        "safesearch": "true",
        "image_type": "photo",
        "per_page": 200,
        "page": starting_page
    }

    if not check_images_exist(general_api_call, url, params):
        logging.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def pixabay_image_selector(data):
        return data.get('hits', [])

    params['url'] = url

    return download_image_batch(
        general_api_call, api_name, params, None, 'pixabay', pixabay_image_selector,
        category_folder, master_attributes, max_images_per_term, rate_limits
    )


def download_from_unsplash(term, master_attributes, starting_page=1, api_key=None, max_images_per_term=100,
                           rate_limits=None):
    api_name = 'unsplash'
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {
        "query": term,
        "per_page": 30,
        "page": starting_page
    }

    if not check_images_exist(general_api_call, url, params, headers):
        logging.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def unsplash_image_selector(data):
        return data.get('results', [])

    params['url'] = url

    return download_image_batch(
        general_api_call, api_name, params, headers, 'unsplash', unsplash_image_selector,
        category_folder, master_attributes, max_images_per_term, rate_limits
    )


def download_from_pexels(term, master_attributes, starting_page=1, api_key=None, max_images_per_term=100,
                         rate_limits=None):
    logging.debug(f'Starting download from Pexels with term: {term}')
    api_name = 'pexels'
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {
        "query": term,
        "per_page": 80,
        "page": starting_page
    }

    if not check_images_exist(general_api_call, url, params, headers):
        logging.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)
    logging.debug(f'Category folder for Pexels: {category_folder}')

    def pexels_image_selector(data):
        return data.get('photos', [])

    params['url'] = url

    total_downloaded = download_image_batch(
        general_api_call, api_name, params, headers, 'pexels', pexels_image_selector,
        category_folder, master_attributes, max_images_per_term, rate_limits
    )

    return total_downloaded


def download_from_flickr(term, master_attributes, starting_page=1, api_key=None, max_images_per_term=100,
                         rate_limits=None):
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
        "page": starting_page
    }

    if not check_images_exist(general_api_call, url, params):
        logging.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def flickr_image_selector(data):
        return data.get('photos', {}).get('photo', [])

    params['url'] = url

    return download_image_batch(
        general_api_call, api_name, params, None, 'flickr', flickr_image_selector,
        category_folder, master_attributes, max_images_per_term, rate_limits
    )


def download_from_google_cse(term, master_attributes, starting_page=1, api_key=None, search_engine_id=None,
                             max_images_per_term=100, rate_limits=None):
    api_name = 'google_cse'
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": term,
        "searchType": "image",
        "num": 10,
        "start": (starting_page - 1) * 10 + 1
    }

    if not check_images_exist(general_api_call, url, params):
        logging.info(f"No images found for term '{term}' from {api_name}")
        return 0

    category_folder = get_category_folder(api_name, term)

    def google_cse_image_selector(data):
        return data.get('items', [])

    def extract_image_id(image):
        return image.get('title', str(hash(image.get('link'))))

    params['url'] = url

    def download_image_batch_google_cse(api_call_function, api_name, params, headers, file_prefix, image_selector,
                                        category_folder, master_attributes, max_images_per_term, rate_limits):
        futures = []
        total_downloaded = 0
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=8) as executor:
            with tqdm(total=max_images_per_term, desc=f"Downloading from {api_name}") as pbar:
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

                        image_id = extract_image_id(image)
                        if is_duplicate_image(image_id, master_attributes):
                            logging.info(f"Duplicate image found, skipping: {image_id}")
                            continue

                        image_url = image.get('link')
                        if not image_url:
                            continue

                        ensure_directory_exists(category_folder)

                        file_name = f"{file_prefix}_{image_id}.jpg"
                        file_path = os.path.join(category_folder, file_name)
                        futures.append(executor.submit(download_image, image_url, file_path))
                        save_metadata(api_name, image_id, image, category_folder, master_attributes)
                        total_downloaded += 1
                        pbar.update(1)

                    params['start'] += 10

            for future in as_completed(futures):
                future.result()

        METRICS['total_images_downloaded'] += total_downloaded
        METRICS['images_per_category'][category_folder] += total_downloaded
        METRICS['api_times'][api_name] += time.time() - start_time

        return total_downloaded

    return download_image_batch_google_cse(
        general_api_call, api_name, params, None, 'google_cse', google_cse_image_selector,
        category_folder, master_attributes, max_images_per_term, rate_limits
    )


# Define a mapping for API name-to-function
API_FUNCTIONS = {
    'pixabay': {'func': download_from_pixabay, 'name': 'pixabay'},
    'unsplash': {'func': download_from_unsplash, 'name': 'unsplash'},
    'pexels': {'func': download_from_pexels, 'name': 'pexels'},
    'flickr': {'func': download_from_flickr, 'name': 'flickr'},
    'google_cse': {'func': download_from_google_cse, 'name': 'google_cse'}
}


def download_images(api_function_mapping, search_terms, master_attributes, max_images_per_term):
    for term in search_terms:
        for api_key, api_info in api_function_mapping.items():
            api_func = api_info['func']
            api_name = api_info['name']

            logging.info(f'Starting download from {api_name} for term: {term}')

            # API specific arguments
            api_args = {
                'term': term,
                'master_attributes': master_attributes,
                'starting_page': 1,
                'api_key': config['api_keys'][api_name]['key'],
                'max_images_per_term': max_images_per_term,
                'rate_limits': config.get('rate_limits', {}).get(api_name),
            }

            if api_name == 'google_cse':
                api_args['search_engine_id'] = config['api_keys'][api_name]["search_engine_id"]

            total_downloaded = api_func(**api_args)
            logging.info(f'Total images downloaded from {api_name} for term "{term}": {total_downloaded}')


def send_email_notification(email_address, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = config['email_settings']['from_email']
    msg['To'] = email_address

    try:
        with smtplib.SMTP(config['email_settings']['smtp_server'], config['email_settings']['smtp_port']) as s:
            s.login(config['email_settings']['smtp_login'], config['email_settings']['smtp_password'])
            s.send_message(msg)
            logging.info('Email notification sent successfully.')
    except Exception as e:
        logging.error(f'Failed to send email notification: {e}')


def main():
    global config
    parser = argparse.ArgumentParser(description='Download images from APIs.')
    parser.add_argument('--config', type=str, help='Path to the configuration file.')
    parser.add_argument('--email', '-e', type=str, choices=['on', 'off'], default='off',
                        help='Enable email notifications (default is off).')

    args = parser.parse_args()

    config_path = args.config or 'config.yaml'
    config = load_config(config_path)
    ensure_directory_exists(BASE_DIR)

    master_attributes = load_master_attributes('pixelbay')

    search_terms = config.get('search_terms', DEFAULT_SEARCH_TERMS)
    max_images_per_term = config.get('max_images_per_term', 1)

    download_images(API_FUNCTIONS, search_terms, master_attributes, max_images_per_term)

    save_master_attributes('pixabay', master_attributes)

    if args.email == 'on':
        subject = 'Image Download Report'
        body = f"""
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Total images downloaded: {METRICS['total_images_downloaded']}
        Images per category: {json.dumps(METRICS['images_per_category'], indent=2)}
        Total requests made: {METRICS['total_requests_made']}
        Successful requests: {METRICS['successful_requests']}
        Failed requests: {METRICS['failed_requests']}
        API time spent: {json.dumps(METRICS['api_times'], indent=2)}
        API retries: {json.dumps(METRICS['api_retries'], indent=2)}
        """
        send_email_notification(config['email_settings']['to_email'], subject, body)


if __name__ == '__main__':
    main()
