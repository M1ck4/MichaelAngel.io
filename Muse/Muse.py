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

# Configure logging
logging.basicConfig(
    filename='muse_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
            logging.info(f'Loaded metadata from {json_file}')
        except Exception as e:
            logging.error(f'Error loading metadata from {json_file}: {e}')
    return metadata_list

def quality_control(item: Dict[str, Any], min_size: int, allowed_formats: List[str]) -> bool:
    """Check image quality and format."""
    image_path = item.get('Filepath')
    try:
        with Image.open(image_path) as img:
            if img.format not in allowed_formats:
                logging.warning(f'Image {image_path} has unsupported format {img.format}.')
                return False
            if img.width < min_size or img.height < min_size:
                logging.warning(f'Image {image_path} is too small ({img.width}x{img.height}).')
                return False
        return True
    except Exception as e:
        logging.error(f'Error during quality control for {image_path}: {e}')
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
        logging.info(f'Applied augmentations to {image_path}')
    except Exception as e:
        logging.error(f'Error augmenting image {image_path}: {e}')
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

def main(args):
    # Load metadata from preprocessed images
    metadata_list = load_metadata(args.input_folder)

    # Quality control
    metadata_list = [
        item for item in metadata_list
        if quality_control(item, args.min_size, args.allowed_formats)
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
    label_mapping = {
        'Category1': 0,
        'Category2': 1,
        'Unknown': -1
    }

    # Apply labels
    for item in metadata_list:
        category = item.get('Category', 'Unknown')
        label = label_mapping.get(category, label_mapping.get('Unknown', -1))
        item['Label'] = label

    # Split the dataset
    dataset_splits = split_dataset(metadata_list, args.split_ratios, stratify=args.stratify)

    # Data augmentation (if enabled)
    if args.augment:
        augmentation_types = args.augmentation_types
        dataset_splits = augment_dataset(dataset_splits, augmentation_types, args.augmentation_multiplier)

    # Analyze dataset
    analyze_dataset(dataset_splits)

    # Export the dataset
    export_dataset(dataset_splits, args.output_folder)

    logging.info('Muse processing completed.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Muse Dataset Creation and Management Tool")
    parser.add_argument('--input_folder', type=str, required=True,
                        help='Path to the input folder containing preprocessed images from Chisel.')
    parser.add_argument('--output_folder', type=str, required=True,
                        help='Path to the output folder for the dataset.')
    parser.add_argument('--split_ratios', type=float, nargs=3, default=(0.8, 0.1, 0.1),
                        help='Split ratios for training, validation, and test sets (sum must be 1.0).')
    parser.add_argument('--augment', action='store_true',
                        help='Enable data augmentation.')
    parser.add_argument('--augmentation_types', type=str, nargs='*',
                        default=['rotate', 'flip_horizontal', 'mixup', 'cutmix'],
                        help='Types of augmentations to apply.')
    parser.add_argument('--augmentation_multiplier', type=int, default=1,
                        help='Number of times to apply augmentation per image.')
    parser.add_argument('--min_size', type=int, default=128,
                        help='Minimum image size for quality control.')
    parser.add_argument('--allowed_formats', type=str, nargs='*', default=['JPEG', 'PNG'],
                        help='Allowed image formats.')
    parser.add_argument('--stratify', action='store_true',
                        help='Enable stratified splitting based on labels.')

    args = parser.parse_args()
    main(args)
