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
import imagehash  # For perceptual hashing

# Import Metaforge components
from metaforge.metadata_manager import Metaforge
from metaforge.schemas import ImageProcessingMetadataSchema

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# Create handlers
log_file_path = 'chisel.log'
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def load_config(config_path: str = "config.yaml") -> dict:
    """ Load configuration from YAML file with error handling. """
    config = {}
    if Path(config_path).exists():
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                if not isinstance(config, dict):
                    raise ValueError("Configuration file is malformed.")
                logger.debug('Configuration loaded successfully.')
        except yaml.YAMLError as e:
            logger.error(f"Error parsing the configuration file: {e}")
            sys.exit(f"Error parsing the configuration file: {e}")
    else:
        logger.error(f"Configuration file {config_path} not found.")
        sys.exit(f"Configuration file {config_path} not found.")
    return config


def is_image_quality_good(image_path: str, min_size: int, blur_threshold: float) -> bool:
    """ Check the quality of an image based on size and blurriness. """
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.warning(f"Failed to read image {image_path}.")
            return False

        height, width = image.shape[:2]
        if height < min_size or width < min_size:
            logger.info(f'Image {image_path} is too small.')
            return False

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < blur_threshold:
            logger.info(f'Image {image_path} is too blurry. Variance: {variance}')
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking quality for {image_path}: {e}")
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
        logger.debug(f'Extracted metadata from {image_path}: {metadata}')
    except Exception as e:
        logger.warning(f'Could not extract metadata from {image_path}: {e}')
    return metadata


def extract_attribution(image_path: str) -> Dict:
    """ Extract or assign attribution information (author, license). """
    # Placeholder function - implement actual attribution extraction if available
    attribution = {
        "author": "Unknown",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "source": image_path
    }
    return attribution


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
            logger.debug(f'Processed image {image_path}')
            return processed_image, extract_metadata(image_path)
    except Exception as e:
        logger.error(f'Error processing {image_path}: {e}')
        return None, {}


def compute_image_hash(image_path: str) -> str:
    """ Compute a perceptual hash of the image content for duplicate detection. """
    try:
        with Image.open(image_path) as img:
            hash_value = str(imagehash.average_hash(img))
            return hash_value
    except Exception as e:
        logger.error(f"Error hashing image {image_path}: {e}")
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
            logger.info(f'Removing duplicate image: {img_path}')
            try:
                img_path.unlink()
                logger.debug(f'Removed duplicate image: {img_path}')
            except Exception as e:
                logger.error(f"Error removing duplicate image {img_path}: {e}")


def determine_category_folder(img_path: str, output_folder: str) -> Path:
    """ Determine the output subfolder based on image source or other criteria. """
    # Placeholder for determining category - implement actual logic as needed
    # For example, categorize based on filename patterns, metadata, etc.
    category_folder = 'processed_other_images'  # Default category
    category_output_folder = Path(output_folder) / category_folder
    category_output_folder.mkdir(parents=True, exist_ok=True)
    return category_output_folder


def process_single_image(args: Tuple[str, str, Tuple[int, int], str, int, float, Tuple[float, float, float, float], int, Metaforge]) -> Dict:
    """ Process a single image and save the results, including attribution and metadata. """
    (img_path, output_folder, target_size, output_format, min_size, blur_threshold,
     enhancement_factors, quality, metaforge) = args

    if not is_image_quality_good(img_path, min_size, blur_threshold):
        logger.info(f'Skipping low-quality image: {img_path}')
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
            logger.debug(f'Saved processed image to {output_path}')
        except Exception as e:
            logger.error(f'Error saving processed image {output_path}: {e}')
            return {}

        # Collect metadata and attribution in a single dictionary
        attribution = extract_attribution(img_path)
        metadata['attribution'] = attribution
        metadata['processing_steps'] = [
            {
                "step": "Preprocessing",
                "actions": {
                    "resized_to": target_size,
                    "output_format": output_format,
                    "enhancement_factors": {
                        "brightness": enhancement_factors[0],
                        "contrast": enhancement_factors[1],
                        "color": enhancement_factors[2],
                        "sharpness": enhancement_factors[3]
                    },
                    "quality": quality
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

        # Create ImageProcessingMetadataSchema instance
        processing_metadata = ImageProcessingMetadataSchema(
            image_id=Path(img_path).stem,
            source_image_path=img_path,
            processed_image_path=str(output_path),
            download_timestamp=metadata.get('download_info', {}).get('download_timestamp', datetime.utcnow()),
            processing_steps=metadata.get('processing_steps', []),
            attribution=attribution,
            extracted_metadata=metadata
        )

        # Add processing metadata to Metaforge (SQL Database)
        metaforge.add_image_processing_metadata(processing_metadata)

        # Append metadata to a JSON file for the category
        json_file_path = category_output_folder / 'metadata.json'
        try:
            if json_file_path.exists():
                with open(json_file_path, 'r') as json_file:
                    all_metadata = json.load(json_file)
            else:
                all_metadata = []

            all_metadata.append(processing_metadata.dict())

            with open(json_file_path, 'w') as json_file:
                json.dump(all_metadata, json_file, indent=2)
            logger.debug(f'Appended metadata to {json_file_path}')
        except Exception as e:
            logger.error(f'Error writing metadata to {json_file_path}: {e}')
            return {}

        logger.info(f'Successfully processed and saved {img_path}')
        return processing_metadata.dict()
    return {}


def preprocess_images(image_folder: str, output_folder: str, target_size: Tuple[int, int],
                     output_format: str, min_size: int, blur_threshold: float,
                     enhancement_factors: Tuple[float, float, float, float], quality: int,
                     supported_formats: List[str], metaforge: Metaforge) -> None:
    """ Preprocess images: remove duplicates, resize, enhance, normalize, and save. """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    logger.info(f'Starting preprocessing for images in {image_folder}')

    remove_duplicates(image_folder, supported_formats)

    image_paths = [str(p) for p in Path(image_folder).rglob('*') if p.suffix.lower() in supported_formats]
    tasks = [
        (img, output_folder, target_size, output_format, min_size, blur_threshold, enhancement_factors, quality, metaforge)
        for img in image_paths
    ]

    # Parallel processing with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_single_image, task) for task in tasks]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Processing Images'):
            try:
                result = future.result()
                if result:
                    logger.debug(f'Processed image result: {result}')
            except Exception as e:
                logger.error(f"Error during image processing: {e}")


def main():
    parser = argparse.ArgumentParser(description="Image Preprocessing Script")
    parser.add_argument('--image_folder', type=str, help='Path to the input folder containing images.')
    parser.add_argument('--output_folder', type=str, help='Path to the output folder for processed images.')
    parser.add_argument('--target_size', type=int, nargs=2, help='Target size for image resizing (width height).')
    parser.add_argument('--output_format', type=str, choices=['JPEG', 'PNG', 'numpy'], help='Output format for processed images.')
    parser.add_argument('--min_size', type=int, help='Minimum size (in pixels) for image quality.')
    parser.add_argument('--blur_threshold', type=float, help='Blur threshold for image quality check.')
    parser.add_argument('--enhancement_factors', type=float, nargs=4, help='Enhancement factors for brightness, contrast, color, and sharpness.')
    parser.add_argument('--quality', type=int, help='Quality for JPEG output (1-100).')
    parser.add_argument('--config_path', type=str, default='config.yaml', help='Path to the configuration YAML file.')
    parser.add_argument('--supported_formats', type=str, nargs='+', help='List of supported image formats.')

    cli_args = parser.parse_args()

    # Load YAML config if available
    config = load_config(cli_args.config_path)

    # Merge configurations with CLI arguments (CLI has higher precedence)
    final_config = {
        'paths': config.get('paths', {}),
        'target': config.get('target', {}),
        'quality_control': config.get('quality_control', {}),
        'enhancement': config.get('enhancement', {}),
        'output': config.get('output', {}),
        'duplicate_detection': config.get('duplicate_detection', {}),
        'threads': config.get('threads', {}),
        'logging': config.get('logging', {}),
        'duplicate_handling': config.get('duplicate_handling', {}),
        'database': config.get('database', {}),
        'metadata_export': config.get('metadata_export', {})
    }

    # Override with CLI arguments if provided
    if cli_args.image_folder:
        final_config['paths']['image_folder'] = cli_args.image_folder
    if cli_args.output_folder:
        final_config['paths']['output_folder'] = cli_args.output_folder
    if cli_args.target_size:
        final_config['target']['size'] = cli_args.target_size
    if cli_args.output_format:
        final_config['target']['format'] = cli_args.output_format
    if cli_args.min_size:
        final_config['quality_control']['min_size'] = cli_args.min_size
    if cli_args.blur_threshold:
        final_config['quality_control']['blur_threshold'] = cli_args.blur_threshold
    if cli_args.enhancement_factors:
        final_config['enhancement'] = {
            'brightness': cli_args.enhancement_factors[0],
            'contrast': cli_args.enhancement_factors[1],
            'color': cli_args.enhancement_factors[2],
            'sharpness': cli_args.enhancement_factors[3]
        }
    if cli_args.quality:
        final_config['output']['quality'] = cli_args.quality
    if cli_args.supported_formats:
        final_config['duplicate_detection']['supported_formats'] = cli_args.supported_formats

    # Initialize Metaforge with database URL from config
    metaforge = Metaforge(db_url=final_config['database'].get('url', 'sqlite:///metaforge.db'))

    # Preprocess images using final configuration
    preprocess_images(
        image_folder=final_config['paths']['image_folder'],
        output_folder=final_config['paths']['output_folder'],
        target_size=tuple(final_config['target']['size']),
        output_format=final_config['target']['format'],
        min_size=final_config['quality_control']['min_size'],
        blur_threshold=final_config['quality_control']['blur_threshold'],
        enhancement_factors=(
            final_config['enhancement']['brightness'],
            final_config['enhancement']['contrast'],
            final_config['enhancement']['color'],
            final_config['enhancement']['sharpness']
        ),
        quality=final_config['output']['quality'],
        supported_formats=final_config['duplicate_detection']['supported_formats'],
        metaforge=metaforge
    )

    # Export metadata
    export_dir = final_config['metadata_export'].get('export_dir', 'metaforge/exports/chisel')
    Path(export_dir).mkdir(parents=True, exist_ok=True)
    metaforge.export_metadata(['json', 'yaml'], export_dir=export_dir)

    logger.info("Image preprocessing completed successfully.")

    # Close Metaforge connection
    metaforge.close_connection()


if __name__ == "__main__":
    main()
