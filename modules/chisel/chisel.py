import os
import sys
import json
import logging
import argparse
import yaml
from pathlib import Path
from typing import Tuple, Dict, Optional, List
from PIL import Image, ExifTags, ImageEnhance
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from tqdm import tqdm
import imagehash  # Added for perceptual hashing

# Configure logging
logging.basicConfig(
    filename='preprocessing_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path: str = "config.yaml") -> dict:
    """ Load configuration from YAML file with error handling. """
    config = {}
    if Path(config_path).exists():
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                if not isinstance(config, dict):
                    raise ValueError("Configuration file is malformed.")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing the configuration file: {e}")
            sys.exit(f"Error parsing the configuration file: {e}")
    else:
        logging.warning(f"Configuration file {config_path} not found. Using default settings.")
    return config

def merge_configs(defaults: dict, config: dict, cli_args: argparse.Namespace) -> dict:
    """ Merge default values, config file values, and CLI arguments (in order of precedence). """
    # Start with defaults
    merged = defaults.copy()
    # Override with YAML config
    merged.update(config)
    # Override with CLI arguments if provided
    cli_dict = vars(cli_args)
    for key, value in cli_dict.items():
        if value is not None:
            merged[key] = value
    return merged

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
    """ Compute a perceptual hash of the image content for duplicate detection. """
    try:
        with Image.open(image_path) as img:
            hash_value = str(imagehash.average_hash(img))
            return hash_value
    except Exception as e:
        logging.error(f"Error hashing image {image_path}: {e}")
        return ""

def remove_duplicates(image_folder: str, supported_formats: List[str]) -> None:
    """ Remove duplicate images from the specified folder based on perceptual hash. """
    image_files = [p for p in Path(image_folder).rglob('*') if p.suffix.lower() in supported_formats]
    unique_hashes = set()
    for img_path in image_files:
        img_hash = compute_image_hash(str(img_path))
        if img_hash and img_hash not in unique_hashes:
            unique_hashes.add(img_hash)
        else:
            logging.info(f'Removing duplicate image: {img_path}')
            try:
                img_path.unlink()
            except Exception as e:
                logging.error(f"Error removing duplicate image {img_path}: {e}")

def determine_category_folder(img_path: str, output_folder: str) -> Path:
    """ Determine the output subfolder based on image source. """
    if 'flickr_images_abstract' in str(img_path):
        category_folder = 'processed_flickr_images_abstract'
    else:
        category_folder = 'processed_other_images'  # Default category
    category_output_folder = Path(output_folder) / category_folder
    category_output_folder.mkdir(parents=True, exist_ok=True)
    return category_output_folder

def process_single_image(args: Tuple[str, str, Tuple[int, int], str, int, float, Tuple[float, float, float, float], int]) -> Dict:
    """ Process a single image and save the results, including attribution. """
    (img_path, output_folder, target_size, output_format, min_size, blur_threshold,
     enhancement_factors, quality) = args

    if not is_image_quality_good(img_path, min_size, blur_threshold):
        logging.info(f'Skipping low-quality image: {img_path}')
        return {}

    processed_image, metadata = preprocess_image(img_path, target_size, output_format, enhancement_factors, quality)
    if processed_image is not None:
        category_output_folder = determine_category_folder(img_path, output_folder)
        output_filename = f'{Path(img_path).stem}.{output_format.lower() if output_format != "numpy" else "npy"}'
        output_path = category_output_folder / output_filename

        try:
            if output_format == 'numpy':
                np.save(output_path, processed_image)
            else:
                processed_image.save(output_path, format=output_format, quality=quality, optimize=True)
        except Exception as e:
            logging.error(f'Error saving processed image {output_path}: {e}')
            return {}

        # Collect metadata and attribution in a single dictionary
        attribution = extract_attribution(img_path)
        metadata['Attribution'] = attribution

        # Append metadata and attribution to a JSON file for the category
        json_file_path = category_output_folder / 'metadata.json'
        try:
            if json_file_path.exists():
                with open(json_file_path, 'r') as json_file:
                    all_metadata = json.load(json_file)
            else:
                all_metadata = []

            all_metadata.append(metadata)

            with open(json_file_path, 'w') as json_file:
                json.dump(all_metadata, json_file, indent=2)
        except Exception as e:
            logging.error(f'Error writing metadata to {json_file_path}: {e}')
            return {}

        logging.info(f'Successfully processed and saved {img_path}')
        return {**metadata, 'Filename': Path(img_path).name, 'Attribution': attribution}
    return {}

def preprocess_images(image_folder: str, output_folder: str, target_size: Tuple[int, int],
                      output_format: str, min_size: int, blur_threshold: float,
                      enhancement_factors: Tuple[float, float, float, float], quality: int,
                      supported_formats: List[str]) -> None:
    """ Preprocess images: remove duplicates, resize, enhance, normalize, and save. """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    logging.info(f'Starting preprocessing for images in {image_folder}')

    remove_duplicates(image_folder, supported_formats)

    image_paths = [str(p) for p in Path(image_folder).rglob('*') if p.suffix.lower() in supported_formats]
    tasks = [
        (img, output_folder, target_size, output_format, min_size, blur_threshold, enhancement_factors, quality)
        for img in image_paths
    ]

    # Parallel processing with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
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
    parser.add_argument('--image_folder', type=str, default='./images',
                        help='Path to the input folder containing images (default: ./images).')
    parser.add_argument('--output_folder', type=str, default='./processed_images',
                        help='Path to the output folder for processed images (default: ./processed_images).')
    parser.add_argument('--target_size', type=int, nargs=2, default=(256, 256),
                        help='Target size for image resizing (width height) (default: 256 256).')
    parser.add_argument('--output_format', type=str, choices=['JPEG', 'PNG', 'numpy'], default='JPEG',
                        help='Output format for processed images (default: JPEG).')
    parser.add_argument('--min_size', type=int, default=128,
                        help='Minimum size (in pixels) for image quality (default: 128).')
    parser.add_argument('--blur_threshold', type=float, default=100.0,
                        help='Blur threshold for image quality check (default: 100.0).')
    parser.add_argument('--enhancement_factors', type=float, nargs=4, default=(1.0, 1.0, 1.0, 1.0),
                        help='Enhancement factors for brightness, contrast, color, and sharpness (default: 1.0 1.0 1.0 1.0).')
    parser.add_argument('--quality', type=int, default=85,
                        help='Quality for JPEG output (1-100) (default: 85).')
    parser.add_argument('--config_path', type=str, default='config.yaml',
                        help='Path to the configuration YAML file (default: config.yaml).')
    parser.add_argument('--supported_formats', type=str, nargs='+', default=['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
                        help='List of supported image formats (default: .jpg .jpeg .png .bmp .tiff).')

    cli_args = parser.parse_args()

    # Validate CLI arguments
    if not 1 <= cli_args.quality <= 100:
        parser.error("Quality must be between 1 and 100.")

    # Default settings
    defaults = {
        'image_folder': './images',
        'output_folder': './processed_images',
        'target_size': (256, 256),
        'output_format': 'JPEG',
        'min_size': 128,
        'blur_threshold': 100.0,
        'enhancement_factors': (1.0, 1.0, 1.0, 1.0),
        'quality': 85,
        'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    }

    # Load YAML config if available
    config = load_config(cli_args.config_path)

    # Merge configurations
    final_config = merge_configs(defaults, config, cli_args)

    # Preprocess images using final configuration
    preprocess_images(
        final_config['image_folder'],
        final_config['output_folder'],
        tuple(final_config['target_size']),
        final_config['output_format'],
        final_config['min_size'],
        final_config['blur_threshold'],
        tuple(final_config['enhancement_factors']),
        final_config['quality'],
        final_config['supported_formats']
    )
