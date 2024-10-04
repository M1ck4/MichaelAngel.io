import os
import json
import time
import logging
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# API keys (replace with your actual keys)
API_KEYS = {
    'pixabay': 'YOUR_PIXABAY_API_KEY',
    'unsplash': 'YOUR_UNSPLASH_API_KEY',
    'pexels': 'YOUR_PEXELS_API_KEY',
    'flickr': 'YOUR_FLICKR_AP_KEY'
}

# Search terms
SEARCH_TERMS = ["abstract", "character", "fantasy", "landscape", "urban", "nature", "cities",
                "futuristic", "stylized", "surrealism", "impressionism", "pop", "deco", "concept"]

# Configure logging
logging.basicConfig(filename='image_downloader.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def setup_folder(api, term):
    folder_name = f"{api}_images_{term}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def load_downloaded_images(api, term):
    file_name = f"{api}_{term}_downloaded.json"
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return set(json.load(f))
    return set()


def save_downloaded_images(api, term, downloaded):
    file_name = f"{api}_{term}_downloaded.json"
    with open(file_name, 'w') as f:
        json.dump(list(downloaded), f)


def download_image(url, path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        logging.error(f"Error downloading {url}: {str(e)}")
        return False


def save_attribution(api, image_id, attribution, folder):
    with open(os.path.join(folder, f"{api}_{image_id}_attribution.json"), 'w') as f:
        json.dump(attribution, f)


def download_from_pixabay(term, folder, downloaded, max_images):
    url = "https://pixabay.com/api/"
    params = {
        "key": API_KEYS['pixabay'],
        "q": term,
        "image_type": "photo",
        "per_page": 200,
        "page": 1
    }
    total_downloaded = 0

    with tqdm(total=max_images, desc=f"Downloading from Pixabay: {term}") as pbar:
        while total_downloaded < max_images:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data['hits']:
                    break

                for image in data['hits']:
                    if total_downloaded >= max_images:
                        break

                    if str(image['id']) not in downloaded:
                        image_url = image['largeImageURL']
                        file_name = f"pixabay_{image['id']}.jpg"
                        file_path = os.path.join(folder, file_name)

                        if download_image(image_url, file_path):
                            downloaded.add(str(image['id']))
                            save_attribution('pixabay', image['id'], image, folder)
                            total_downloaded += 1
                            pbar.update(1)

                params['page'] += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error in Pixabay API request: {str(e)}")
                break

    return total_downloaded


def download_from_unsplash(term, folder, downloaded, max_images):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "client_id": API_KEYS['unsplash'],
        "query": term,
        "per_page": 30,
        "page": 1
    }
    total_downloaded = 0

    with tqdm(total=max_images, desc=f"Downloading from Unsplash: {term}") as pbar:
        while total_downloaded < max_images:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data['results']:
                    break

                for image in data['results']:
                    if total_downloaded >= max_images:
                        break

                    if image['id'] not in downloaded:
                        image_url = image['urls']['raw']
                        file_name = f"unsplash_{image['id']}.jpg"
                        file_path = os.path.join(folder, file_name)

                        if download_image(image_url, file_path):
                            downloaded.add(image['id'])
                            save_attribution('unsplash', image['id'], image, folder)
                            total_downloaded += 1
                            pbar.update(1)

                params['page'] += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error in Unsplash API request: {str(e)}")
                break

    return total_downloaded


def download_from_pexels(term, folder, downloaded, max_images):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": API_KEYS['pexels']}
    params = {
        "query": term,
        "per_page": 80,
        "page": 1
    }
    total_downloaded = 0

    with tqdm(total=max_images, desc=f"Downloading from Pexels: {term}") as pbar:
        while total_downloaded < max_images:
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if not data['photos']:
                    break

                for image in data['photos']:
                    if total_downloaded >= max_images:
                        break

                    if str(image['id']) not in downloaded:
                        image_url = image['src']['original']
                        file_name = f"pexels_{image['id']}.jpg"
                        file_path = os.path.join(folder, file_name)

                        if download_image(image_url, file_path):
                            downloaded.add(str(image['id']))
                            save_attribution('pexels', image['id'], image, folder)
                            total_downloaded += 1
                            pbar.update(1)

                params['page'] += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error in Pexels API request: {str(e)}")
                break

    return total_downloaded


def download_from_flickr(term, folder, downloaded, max_images):
    url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": API_KEYS['flickr'],
        "text": term,
        "license": "4,5,7,8,9,10",  # Creative Commons licenses
        "format": "json",
        "nojsoncallback": 1,
        "per_page": 50,
        "page": 1
    }
    total_downloaded = 0
    hourly_limit = 50
    start_time = datetime.now()

    with tqdm(total=min(max_images, hourly_limit), desc=f"Downloading from Flickr: {term}") as pbar:
        while total_downloaded < max_images:
            if total_downloaded >= hourly_limit:
                # Wait until an hour has passed since start_time
                wait_time = (start_time + timedelta(hours=1)) - datetime.now()
                if wait_time.total_seconds() > 0:
                    logging.info(f"Reached Flickr hourly limit. Waiting for {wait_time.total_seconds()} seconds.")
                    time.sleep(wait_time.total_seconds())
                start_time = datetime.now()
                total_downloaded = 0
                pbar.reset(min(max_images - total_downloaded, hourly_limit))

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'photos' not in data or 'photo' not in data['photos'] or not data['photos']['photo']:
                    break

                for photo in data['photos']['photo']:
                    if total_downloaded >= max_images:
                        break

                    if photo['id'] not in downloaded:
                        image_url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg"
                        file_name = f"flickr_{photo['id']}.jpg"
                        file_path = os.path.join(folder, file_name)

                        if download_image(image_url, file_path):
                            downloaded.add(photo['id'])
                            save_attribution('flickr', photo['id'], photo, folder)
                            total_downloaded += 1
                            pbar.update(1)

                params['page'] += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error in Flickr API request: {str(e)}")
                break

    return total_downloaded


def download_images(api, term, max_images=10000):
    folder = setup_folder(api, term)
    downloaded = load_downloaded_images(api, term)

    if api == 'pixabay':
        total_downloaded = download_from_pixabay(term, folder, downloaded, max_images)
    elif api == 'unsplash':
        total_downloaded = download_from_unsplash(term, folder, downloaded, max_images)
    elif api == 'pexels':
        total_downloaded = download_from_pexels(term, folder, downloaded, max_images)
    elif api == 'flickr':
        total_downloaded = download_from_flickr(term, folder, downloaded, max_images)

    save_downloaded_images(api, term, downloaded)
    logging.info(f"Downloaded {total_downloaded} images for {term} from {api}")


def main():
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for api in API_KEYS.keys():
            for term in SEARCH_TERMS:
                futures.append(executor.submit(download_images, api, term))

        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()
