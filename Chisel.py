import os
import json
import logging
import argparse
from pathlib import Path
from typing import Tuple, Dict, Optional, List
from PIL import Image, ExifTags, ImageEnhance
import numpy as np
import cv2
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    filename='preprocessing_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def is_image_quality_good(image_path: str, min_size: int, blur_threshold: float) -> bool:
    """ Check the quality of an image based on size and blurriness. """
    try:
        image = cv2.imread(image_path)
        if image is None:
            logging.warning(f"Failed to read image {image_path}.")
            return False

        height, width = image.shape[:2]
        if height < min_size or width < min_size:
            logging.info(f'Image {image_path} is too small.')
            return False

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < blur_threshold:
            logging.info(f'Image {image_path} is too blurry. Variance: {variance}')
            return False
        return True
    except Exception as e:
        logging.error(f"Error checking quality for {image_path}: {e}")
        return False


def extract_metadata(image_path: str) -> Dict:
    """ Extract EXIF metadata from the image and general metadata such as size, format, etc. """
    metadata = {}
    try:
        with Image.open(image_path) as image:
            exif_data = image._getexif()
            if exif_data:
                metadata = {
                    ExifTags.TAGS.get(tag, tag): str(value)
                    for tag, value in exif_data.items()
                }
            metadata.update({
                'filename': Path(image_path).name,
                'size': image.size,
                'format': image.format,
                'mode': image.mode
            })
    except Exception as e:
        logging.warning(f'Could not extract metadata from {image_path}: {e}')
    return metadata


def extract_attribution(image_path: str) -> Dict:
    """ Placeholder function to extract attribution information (author, license). """
    attribution = {
        "author": "Unknown",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "source": image_path
    }
    return attribution


def save_attribution(image_path: str, output_folder: str, attribution: Dict) -> None:
    """ Save attribution information to a text file alongside the image. """
    try:
        output_path = Path(output_folder)
        attribution_filename = Path(image_path).stem + '_attribution.txt'
        attribution_filepath = output_path / attribution_filename

        with open(attribution_filepath, 'w') as attribution_file:
            attribution_file.write(f"Image: {attribution['source']}\n")
            attribution_file.write(f"Author: {attribution['author']}\n")
            attribution_file.write(f"License: {attribution['license']}\n")

        logging.info(f'Saved attribution for {image_path} as {attribution_filepath}')
    except Exception as e:
        logging.error(f"Failed to save attribution for {image_path}: {e}")


def enhance_image(image: Image.Image, brightness: float, contrast: float, color: float,
                  sharpness: float) -> Image.Image:
    """ Apply enhancements like brightness, contrast, color, and sharpness to an image. """
    enhancers = [
        (ImageEnhance.Brightness, brightness),
        (ImageEnhance.Contrast, contrast),
        (ImageEnhance.Color, color),
        (ImageEnhance.Sharpness, sharpness)
    ]
    for enhancer_class, factor in enhancers:
        if factor != 1.0:
            enhancer = enhancer_class(image)
            image = enhancer.enhance(factor)
    return image


def preprocess_image(image_path: str, target_size: Tuple[int, int], output_format: str,
                     enhancement_factors: Tuple[float, float, float, float], quality: int) -> Tuple[
    Optional[np.ndarray], Dict]:
    """ Resize, enhance, and normalize an image, returning the processed image and metadata. """
    try:
        with Image.open(image_path) as image:
            image.thumbnail(target_size, Image.LANCZOS)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = enhance_image(image, *enhancement_factors)
            if output_format == 'numpy':
                processed_image = np.array(image) / 255.0
            else:
                processed_image = image
            return processed_image, extract_metadata(image_path)
    except Exception as e:
        logging.error(f'Error processing {image_path}: {e}')
        return None, {}


def compute_image_hash(image_path: str) -> str:
    """ Compute a hash of the image content for duplicate detection. """
    try:
        with open(image_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logging.error(f"Error hashing image {image_path}: {e}")
        return ""


def remove_duplicates(image_folder: str) -> None:
    """ Remove duplicate images from the specified folder based on content hash. """
    image_files = list(Path(image_folder).glob('*'))
    unique_images = {}
    for img_path in image_files:
        img_hash = compute_image_hash(str(img_path))
        if img_hash and img_hash not in unique_images:
            unique_images[img_hash] = img_path
        else:
            logging.info(f'Removing duplicate image: {img_path}')
            try:
                img_path.unlink()
            except Exception as e:
                logging.error(f"Error removing duplicate image {img_path}: {e}")


def process_single_image(
        args: Tuple[str, str, Tuple[int, int], str, int, float, Tuple[float, float, float, float]]) -> Dict:
    """ Process a single image and save the results, including attribution. """
    img_path, output_folder, target_size, output_format, min_size, blur_threshold, enhancement_factors, quality = args
    if not is_image_quality_good(img_path, min_size, blur_threshold):
        logging.info(f'Skipping low-quality image: {img_path}')
        return {}

    processed_image, metadata = preprocess_image(img_path, target_size, output_format, enhancement_factors, quality)
    if processed_image is not None:
        # Determine the output subfolder based on image source
        category_folder = ''
        if 'flickr_images_abstract' in str(img_path):
            category_folder = 'processed_flickr_images_abstract'
        else:
            category_folder = 'processed_other_images'  # Default category

        category_output_folder = Path(output_folder) / category_folder
        category_output_folder.mkdir(parents=True, exist_ok=True)

        output_path = category_output_folder / f'{Path(img_path).stem}.{output_format}'
        if output_format == 'numpy':
            np.save(category_output_folder / f'{Path(img_path).stem}.npy', processed_image)
        else:
            processed_image.save(output_path, quality=quality, optimize=True)

        # Collect metadata and attribution in a single dictionary
        attribution = extract_attribution(img_path)
        metadata['Attribution'] = attribution

        # Append metadata and attribution to a JSON file for the category
        json_file_path = category_output_folder / 'metadata.json'
        if json_file_path.exists():
            with open(json_file_path, 'r') as json_file:
                all_metadata = json.load(json_file)
        else:
            all_metadata = []

        all_metadata.append(metadata)

        with open(json_file_path, 'w') as json_file:
            json.dump(all_metadata, json_file, indent=2)

        logging.info(f'Successfully processed and saved {img_path}')
        return {**metadata, 'Filename': Path(img_path).name, 'Attribution': attribution}
    return {}


def preprocess_images(image_folder: str, output_folder: str, target_size: Tuple[int, int],
                      output_format: str, min_size: int, blur_threshold: float,
                      enhancement_factors: Tuple[float, float, float, float], quality: int) -> None:
    """ Preprocess images: remove duplicates, resize, enhance, normalize, and save. """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    logging.info(f'Starting preprocessing for images in {image_folder}')

    remove_duplicates(image_folder)

    image_paths = list(Path(image_folder).rglob('*'))
    tasks = [
        (str(img), output_folder, target_size, output_format, min_size, blur_threshold, enhancement_factors, quality)
        for img in image_paths]

    # Parallel processing
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_single_image, task) for task in tasks]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Processing Images'):
            try:
                result = future.result()
                if result:
                    logging.info(f'Processed image result: {result}')
            except Exception as e:
                logging.error(f"Error during image processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Preprocessing Script")
    parser.add_argument('--image_folder', type=str, required=True, help='Path to the input folder containing images.')
    parser.add_argument('--output_folder', type=str, required=True,
                        help='Path to the output folder for processed images.')
    parser.add_argument('--target_size', type=int, nargs=2, default=(256, 256),
                        help='Target size for image resizing (width height).')
    parser.add_argument('--output_format', type=str, default='JPEG', choices=['JPEG', 'PNG', 'numpy'],
                        help='Output format for processed images.')
    parser.add_argument('--min_size', type=int, default=128, help='Minimum size (in pixels) for image quality.')
    parser.add_argument('--blur_threshold', type=float, default=100.0, help='Blur threshold for image quality check.')
    parser.add_argument('--enhancement_factors', type=float, nargs=4, default=(1.0, 1.0, 1.0, 1.0),
                        help='Enhancement factors for brightness, contrast, color, and sharpness.')
    parser.add_argument('--quality', type=int, default=85, help='Quality for JPEG output (1-100).')

    args = parser.parse_args()
    preprocess_images(args.image_folder, args.output_folder, args.target_size, args.output_format, args.min_size,
                      args.blur_threshold, args.enhancement_factors, args.quality)
