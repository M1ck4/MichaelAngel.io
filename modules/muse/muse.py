import os
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any
from PIL import Image
from sklearn.model_selection import train_test_split
import logging
import numpy as np
from tqdm import tqdm
import multiprocessing
import random
import yaml
import sys

# Import Metaforge components
from metaforge.metadata_manager import Metaforge
from metaforge.schemas import DatasetMetadataSchema

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# Create handlers
log_file_path = 'muse_log.txt'
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


def load_defaults():
    return {
        'input_folder': 'path/to/preprocessed_images',
        'output_folder': 'path/to/output_dataset',
        'split_ratios': [0.8, 0.1, 0.1],
        'augment': True,
        'augmentation_types': ['rotate', 'flip_horizontal', 'mixup', 'cutmix'],
        'augmentation_multiplier': 1,
        'min_size': 128,
        'allowed_formats': ['JPEG', 'PNG'],
        'stratify': True,
        'label_mapping': {
            'Category1': 0,
            'Category2': 1,
            'Unknown': -1
        },
        'log_file': 'muse_log.txt',
        'log_level': 'INFO',
        'database': {
            'url': 'sqlite:///metaforge.db'
        },
        'metadata_export': {
            'export_dir': 'metaforge/exports/muse'
        }
    }


def load_config(config_file="config.yaml"):
    config = load_defaults()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
                update_dict(config, yaml_config)
                logger.debug(f"Configuration loaded from '{config_file}'.")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing the configuration file: {e}")
            sys.exit(f"Error parsing the configuration file: {e}")
    else:
        logger.warning(f"Configuration file '{config_file}' not found. Using default settings.")
    return config


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def parse_arguments(config):
    parser = argparse.ArgumentParser(description="Muse Dataset Creation and Management Tool")
    parser.add_argument('--input_folder', type=str,
                        help='Path to the input folder containing preprocessed images from Chisel.')
    parser.add_argument('--output_folder', type=str,
                        help='Path to the output folder for the dataset.')
    parser.add_argument('--split_ratios', type=float, nargs=3,
                        help='Split ratios for training, validation, and test sets (sum must be 1.0).')
    parser.add_argument('--augment', action='store_true',
                        help='Enable data augmentation.')
    parser.add_argument('--no-augment', action='store_true',
                        help='Disable data augmentation.')
    parser.add_argument('--augmentation_types', type=str, nargs='*',
                        help='Types of augmentations to apply.')
    parser.add_argument('--augmentation_multiplier', type=int,
                        help='Number of times to apply augmentation per image.')
    parser.add_argument('--min_size', type=int,
                        help='Minimum image size for quality control.')
    parser.add_argument('--allowed_formats', type=str, nargs='*',
                        help='Allowed image formats.')
    parser.add_argument('--stratify', action='store_true',
                        help='Enable stratified splitting based on labels.')
    parser.add_argument('--no-stratify', action='store_true',
                        help='Disable stratified splitting.')
    parser.add_argument('--label_mapping', type=str, nargs='*',
                        help='Mapping of categories to numerical labels in the format Category:Label')
    parser.add_argument('--log_file', type=str,
                        help='Path to the log file.')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level.')
    parser.add_argument('--database_url', type=str,
                        help='Database URL for Metaforge integration.')
    parser.add_argument('--metadata_export_dir', type=str,
                        help='Directory to export metadata JSON/YAML files.')

    args = parser.parse_args()

    # Update config with CLI arguments if provided
    if args.input_folder:
        config['input_folder'] = args.input_folder
    if args.output_folder:
        config['output_folder'] = args.output_folder
    if args.split_ratios:
        config['split_ratios'] = args.split_ratios
    if args.augment:
        config['augment'] = True
    if args.no_augment:
        config['augment'] = False
    if args.augmentation_types:
        config['augmentation_types'] = args.augmentation_types
    if args.augmentation_multiplier is not None:
        config['augmentation_multiplier'] = args.augmentation_multiplier
    if args.min_size is not None:
        config['min_size'] = args.min_size
    if args.allowed_formats:
        config['allowed_formats'] = args.allowed_formats
    if args.stratify:
        config['stratify'] = True
    if args.no_stratify:
        config['stratify'] = False
    if args.label_mapping:
        label_map = {}
        for mapping in args.label_mapping:
            try:
                category, label = mapping.split(':')
                label_map[category] = int(label)
            except ValueError:
                logger.error(f"Invalid label mapping format: {mapping}. Expected format 'Category:Label'.")
        config['label_mapping'].update(label_map)
    if args.log_file:
        config['log_file'] = args.log_file
    if args.log_level:
        config['log_level'] = args.log_level
    if args.database_url:
        config['database']['url'] = args.database_url
    if args.metadata_export_dir:
        config['metadata_export']['export_dir'] = args.metadata_export_dir

    return config


def load_metadata(image_folder: str) -> List[Dict[str, Any]]:
    """Load metadata from JSON files in the image folder."""
    metadata_list = []
    for json_file in Path(image_folder).rglob('metadata.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    # Update 'Filepath' to be absolute path
                    image_filename = item.get('filename')
                    if image_filename:
                        item['Filepath'] = str(Path(json_file).parent / image_filename)
                    item['metadata_path'] = str(json_file)
                metadata_list.extend(data)
            logger.info(f'Loaded metadata from {json_file}')
        except Exception as e:
            logger.error(f'Error loading metadata from {json_file}: {e}')
    return metadata_list


def quality_control(item: Dict[str, Any], min_size: int, allowed_formats: List[str]) -> bool:
    """Check image quality and format."""
    image_path = item.get('Filepath')
    try:
        with Image.open(image_path) as img:
            if img.format not in allowed_formats:
                logger.warning(f'Image {image_path} has unsupported format {img.format}.')
                return False
            if img.width < min_size or img.height < min_size:
                logger.warning(f'Image {image_path} is too small ({img.width}x{img.height}).')
                return False
        return True
    except Exception as e:
        logger.error(f'Error during quality control for {image_path}: {e}')
        return False


def split_dataset(
    metadata_list: List[Dict[str, Any]],
    split_ratios: Tuple[float, float, float],
    stratify: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """Split the dataset into training, validation, and test sets."""
    train_ratio, val_ratio, test_ratio = split_ratios
    if not abs(sum(split_ratios) - 1.0) < 1e-6:
        raise ValueError('Split ratios must sum to 1.0')

    labels = [item.get('Label', -1) for item in metadata_list] if stratify else None

    train_data, temp_data = train_test_split(
        metadata_list, test_size=(1 - train_ratio), stratify=labels, random_state=42)

    if stratify:
        temp_labels = [item.get('Label', -1) for item in temp_data]
    else:
        temp_labels = None

    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_data, test_data = train_test_split(
        temp_data, test_size=(1 - val_ratio_adjusted), stratify=temp_labels, random_state=42)

    logging.info('Dataset split into training, validation, and test sets.')
    return {'train': train_data, 'val': val_data, 'test': test_data}


def apply_labels(
    dataset_splits: Dict[str, List[Dict[str, Any]]],
    label_mapping: Dict[str, int]
) -> Dict[str, List[Dict[str, Any]]]:
    """Apply labels to images based on metadata or defined categories."""
    for split_name, data in dataset_splits.items():
        for item in data:
            category = item.get('Category', 'Unknown')
            label = label_mapping.get(category, label_mapping.get('Unknown', -1))
            item['Label'] = label
    logging.info('Labels applied to dataset.')
    return dataset_splits


def mixup_images(image1: Image.Image, image2: Image.Image, alpha: float = 0.2) -> Image.Image:
    """Apply MixUp augmentation to two images."""
    lam = np.random.beta(alpha, alpha)
    return Image.blend(image1, image2, 1 - lam)


def cutmix_images(image1: Image.Image, image2: Image.Image) -> Image.Image:
    """Apply CutMix augmentation to two images."""
    width, height = image1.size
    cx = np.random.randint(width)
    cy = np.random.randint(height)
    w = width // 2
    h = height // 2

    x0 = np.clip(cx - w // 2, 0, width)
    y0 = np.clip(cy - h // 2, 0, height)
    x1 = np.clip(cx + w // 2, 0, width)
    y1 = np.clip(cy + h // 2, 0, height)

    image1_copy = image1.copy()
    image1_copy.paste(image2.crop((x0, y0, x1, y1)), (x0, y0))
    return image1_copy


def augment_image(
    args
) -> List[Dict[str, Any]]:
    """Apply augmentation techniques to an image (for multiprocessing)."""
    item, data_images, augmentation_types, augmentation_multiplier = args
    augmented_items = []
    image_path = item.get('Filepath')
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')  # Ensure image is in RGB mode
            for _ in range(augmentation_multiplier):
                augmented_images = []
                if 'mixup' in augmentation_types or 'cutmix' in augmentation_types:
                    if len(data_images) < 2:
                        logger.warning('Not enough images for MixUp/CutMix augmentation.')
                        continue
                    other_items = random.sample(data_images, k=1)
                    with Image.open(other_items[0]['Filepath']) as other_img:
                        other_img = other_img.convert('RGB')
                        augmented_images.extend(augment_image_single(img, augmentation_types, other_img))
                else:
                    augmented_images.extend(augment_image_single(img, augmentation_types))
                for idx, aug_img in enumerate(augmented_images):
                    aug_image_name = f"{Path(image_path).stem}_aug_{idx}_{random.randint(0, 1e6)}{Path(image_path).suffix}"
                    aug_image_path = Path(image_path).parent / aug_image_name
                    aug_img.save(aug_image_path)
                    # Copy item and update the filepath
                    aug_item = item.copy()
                    aug_item['Filepath'] = str(aug_image_path)
                    aug_item['Augmentation'] = augmentation_types
                    aug_item['Processing_Steps'] = aug_item.get('Processing_Steps', []) + ['Augmentation']
                    augmented_items.append(aug_item)
        logger.info(f'Applied augmentations to {image_path}')
    except Exception as e:
        logger.error(f'Error augmenting image {image_path}: {e}')
    return augmented_items


def augment_image_single(
    image: Image.Image,
    augmentation_types: List[str],
    additional_image: Image.Image = None
) -> List[Image.Image]:
    """Apply augmentation techniques to a single image."""
    augmented_images = []
    for aug in augmentation_types:
        if aug == 'rotate':
            for angle in [90, 180, 270]:
                augmented_images.append(image.rotate(angle))
        elif aug == 'flip_horizontal':
            augmented_images.append(image.transpose(Image.FLIP_LEFT_RIGHT))
        elif aug == 'flip_vertical':
            augmented_images.append(image.transpose(Image.FLIP_TOP_BOTTOM))
        elif aug == 'crop':
            width, height = image.size
            crop_box = (
                int(width * 0.1), int(height * 0.1),
                int(width * 0.9), int(height * 0.9)
            )
            augmented_images.append(image.crop(crop_box))
        elif aug == 'mixup' and additional_image:
            augmented_images.append(mixup_images(image, additional_image))
        elif aug == 'cutmix' and additional_image:
            augmented_images.append(cutmix_images(image, additional_image))
        # Add more augmentation types as needed
    return augmented_images


def augment_dataset(
    dataset_splits: Dict[str, List[Dict[str, Any]]],
    augmentation_types: List[str],
    augmentation_multiplier: int = 1
) -> Dict[str, List[Dict[str, Any]]]:
    """Apply data augmentation to the dataset using multiprocessing."""
    if 'train' in dataset_splits:
        data = dataset_splits['train']
        data_images = [item for item in data if os.path.exists(item['Filepath'])]
        pool = multiprocessing.Pool()
        tasks = [
            (item, data_images, augmentation_types, augmentation_multiplier)
            for item in data_images
        ]
        augmented_data = []
        for result in tqdm(pool.imap_unordered(augment_image, tasks), total=len(tasks), desc='Augmenting training data'):
            augmented_data.extend(result)
        pool.close()
        pool.join()
        data.extend(augmented_data)
        dataset_splits['train'] = data
        logging.info('Data augmentation completed.')
    else:
        logging.warning('No training data found for augmentation.')
    return dataset_splits


def analyze_dataset(dataset_splits: Dict[str, List[Dict[str, Any]]]) -> None:
    """Provide analytics on the dataset."""
    for split_name, data in dataset_splits.items():
        total_images = len(data)
        label_counts = {}
        for item in data:
            label = item.get('Label', -1)
            label_counts[label] = label_counts.get(label, 0) + 1
        logging.info(f"Dataset split '{split_name}':")
        logging.info(f"  Total images: {total_images}")
        for label, count in label_counts.items():
            logging.info(f"  Label {label}: {count} images")


def export_dataset(
    dataset_splits: Dict[str, List[Dict[str, Any]]],
    output_folder: str
) -> None:
    """Export the dataset to the output folder."""
    for split_name, data in dataset_splits.items():
        split_folder = Path(output_folder) / split_name
        split_folder.mkdir(parents=True, exist_ok=True)
        # Copy images to split folder
        for item in tqdm(data, desc=f'Exporting {split_name} data'):
            image_path = item.get('Filepath')
            try:
                destination = split_folder / Path(image_path).name
                if not destination.exists():
                    os.link(image_path, destination)
                item['Filepath'] = str(destination)
                # Include processing steps in metadata
                item['Processing_Steps'] = item.get('Processing_Steps', []) + ['Exported']
            except Exception as e:
                logging.error(f'Error copying image {image_path} to {split_folder}: {e}')
        # Save metadata
        metadata_file = split_folder / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f'Dataset exported for {split_name} split.')


def store_metadata(
    metadata: Dict[str, Any],
    dataset_split: str,
    split_folder: str,
    metaforge: Metaforge,
    config: Dict[str, Any]
):
    """Store dataset metadata in the database and export files."""
    try:
        # Create DatasetMetadataSchema instance
        dataset_metadata = DatasetMetadataSchema(
            dataset_split=dataset_split,
            dataset_path=split_folder,
            total_images=len(metadata),
            label_distribution={item['Label']: metadata.count(item) for item in metadata},
            processing_steps=['Quality Control', 'Label Application', 'Dataset Splitting', 'Data Augmentation', 'Export']
        )
        # Add to Metaforge
        metaforge.add_dataset_metadata(dataset_metadata)
    except Exception as e:
        logger.error(f"Error storing metadata for split '{dataset_split}': {e}")

    # Export metadata to JSON/YAML files
    try:
        export_formats = config['metadata_export']['export_dir']
        os.makedirs(config['metadata_export']['export_dir'], exist_ok=True)
        for fmt in ['json', 'yaml']:
            file_path = Path(config['metadata_export']['export_dir']) / f"{split_folder}_{dataset_split}_metadata.{fmt}"
            with open(file_path, 'w') as f:
                if fmt == 'json':
                    json.dump(metadata, f, indent=2)
                elif fmt == 'yaml':
                    yaml.dump(metadata, f)
        logger.info(f"Metadata exported for split '{dataset_split}'.")
    except Exception as e:
        logger.error(f"Error exporting metadata for split '{dataset_split}': {e}")


def main(args, config, metaforge):
    # Load metadata from preprocessed images
    metadata_list = load_metadata(config['input_folder'])

    # Quality control
    metadata_list = [
        item for item in metadata_list
        if quality_control(item, config['min_size'], config['allowed_formats'])
    ]

    # Include Creative Commons data
    for item in metadata_list:
        # Assume that the Creative Commons data is in the metadata under 'Attribution'
        attribution = item.get('Attribution', {})
        item['Creative_Commons'] = {
            'Author': attribution.get('author', 'Unknown'),
            'License': attribution.get('license', 'Unknown'),
            'Source': attribution.get('source', 'Unknown')
        }

    # Define label mapping
    label_mapping = config['label_mapping']

    # Apply labels
    dataset_splits = split_dataset(metadata_list, tuple(config['split_ratios']), stratify=config['stratify'])
    dataset_splits = apply_labels(dataset_splits, label_mapping)

    # Data augmentation (if enabled)
    if config['augment']:
        augmentation_types = config['augmentation_types']
        augmentation_multiplier = config['augmentation_multiplier']
        dataset_splits = augment_dataset(dataset_splits, augmentation_types, augmentation_multiplier)

    # Analyze dataset
    analyze_dataset(dataset_splits)

    # Export the dataset
    export_dataset(dataset_splits, config['output_folder'])

    # Store metadata in Metaforge and export
    for split_name, data in dataset_splits.items():
        store_metadata(data, split_name, config['output_folder'], metaforge, config)

    logger.info('Muse processing completed.')

    # Export all metadata to specified directory
    try:
        metaforge.export_metadata(
            formats=['json', 'yaml'],
            export_dir=config['metadata_export']['export_dir']
        )
    except Exception as e:
        logger.error(f"Error exporting metadata: {e}")


if __name__ == "__main__":
    # Load default configurations
    default_config = load_defaults()

    # Load configuration from YAML file or defaults
    config = load_config("config.yaml")

    # Parse command-line arguments and override config
    config = parse_arguments(config)

    # Reconfigure logging if log_file or log_level is updated via CLI
    logger.handlers = []  # Clear existing handlers
    logging.basicConfig(
        filename=config['log_file'],
        level=getattr(logging, config['log_level'].upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Add console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config['log_level'].upper(), logging.INFO))
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    # Initialize Metaforge with database URL from config
    metaforge = Metaforge(db_url=config['database'].get('url', 'sqlite:///metaforge.db'))

    # Run main processing
    main(None, config, metaforge)

    # Close Metaforge connection
    metaforge.close_connection()
