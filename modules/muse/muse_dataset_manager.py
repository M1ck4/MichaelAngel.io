# muse/muse_dataset_manager.py

import logging
from typing import Any, Dict, List
from metaforge import Metaforge, DatasetMetadataSchema
from pathlib import Path
import json
import yaml

logger = logging.getLogger(__name__)

class MuseDatasetManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metaforge = Metaforge(db_url=config['database']['url'])
        logger.debug("MuseDatasetManager initialized.")

    def create_dataset_split(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Split the dataset into training, validation, and test sets.

        Args:
            metadata_list (List[Dict[str, Any]]): List of image metadata dictionaries.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing dataset splits.
        """
        try:
            # Implement splitting logic, possibly using sklearn's train_test_split
            from sklearn.model_selection import train_test_split

            train_ratio, val_ratio, test_ratio = self.config['split_ratios']
            if not abs(sum([train_ratio, val_ratio, test_ratio]) - 1.0) < 1e-6:
                raise ValueError("Split ratios must sum to 1.0")

            train_val, test = train_test_split(
                metadata_list, test_size=test_ratio, random_state=42, stratify=[m['Label'] for m in metadata_list] if self.config.get('stratify') else None
            )
            train, val = train_test_split(
                train_val, test_size=val_ratio / (train_ratio + val_ratio), random_state=42, stratify=[m['Label'] for m in train_val] if self.config.get('stratify') else None
            )

            logger.info("Dataset split into train, validation, and test sets.")
            return {'train': train, 'val': val, 'test': test}
        except Exception as e:
            logger.error(f"Error creating dataset split: {e}")
            raise

    def augment_dataset(self, dataset_splits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Apply data augmentation to the training dataset.

        Args:
            dataset_splits (Dict[str, List[Dict[str, Any]]]): Dataset splits.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Updated dataset splits with augmented data.
        """
        try:
            # Implement augmentation logic, possibly using multiprocessing
            from multiprocessing import Pool
            from tqdm import tqdm

            train_data = dataset_splits.get('train', [])
            augmentation_multiplier = self.config.get('augmentation_multiplier', 1)
            augmentation_types = self.config.get('augmentation_types', [])

            if not augmentation_types:
                logger.warning("No augmentation types specified.")
                return dataset_splits

            with Pool(processes=self.config.get('num_workers', 4)) as pool:
                tasks = [(item, augmentation_types, augmentation_multiplier) for item in train_data]
                results = list(tqdm(pool.imap(self._augment_single, tasks), total=len(tasks), desc="Augmenting training data"))

            augmented_data = [item for sublist in results for item in sublist]
            dataset_splits['train'].extend(augmented_data)
            logger.info("Data augmentation completed.")
            return dataset_splits
        except Exception as e:
            logger.error(f"Error augmenting dataset: {e}")
            raise

    def _augment_single(self, args: tuple) -> List[Dict[str, Any]]:
        """
        Helper function to augment a single image.

        Args:
            args (tuple): Tuple containing the image metadata and augmentation parameters.

        Returns:
            List[Dict[str, Any]]: List of augmented image metadata dictionaries.
        """
        import random
        from PIL import Image, ImageEnhance

        item, augmentation_types, augmentation_multiplier = args
        augmented_items = []
        image_path = item.get('Filepath')

        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                for _ in range(augmentation_multiplier):
                    for aug in augmentation_types:
                        augmented_img = self._apply_augmentation(img, aug)
                        augmented_image_name = f"{Path(image_path).stem}_aug_{random.randint(0, 1e6)}{Path(image_path).suffix}"
                        augmented_image_path = Path(image_path).parent / augmented_image_name
                        augmented_img.save(augmented_image_path)

                        augmented_item = item.copy()
                        augmented_item['Filepath'] = str(augmented_image_path)
                        augmented_item['Augmentation'] = aug
                        augmented_item['Processing_Steps'] = augmented_item.get('Processing_Steps', []) + [aug]
                        augmented_items.append(augmented_item)
            logger.debug(f"Augmented image {image_path} with {len(augmented_items)} new images.")
        except Exception as e:
            logger.error(f"Error augmenting image {image_path}: {e}")

        return augmented_items

    def _apply_augmentation(self, image: Image.Image, augmentation_type: str) -> Image.Image:
        """
        Apply a single augmentation technique to an image.

        Args:
            image (Image.Image): The image to augment.
            augmentation_type (str): The type of augmentation to apply.

        Returns:
            Image.Image: The augmented image.
        """
        try:
            if augmentation_type == 'rotate':
                angle = random.choice([90, 180, 270])
                return image.rotate(angle)
            elif augmentation_type == 'flip_horizontal':
                return image.transpose(Image.FLIP_LEFT_RIGHT)
            elif augmentation_type == 'flip_vertical':
                return image.transpose(Image.FLIP_TOP_BOTTOM)
            elif augmentation_type == 'brightness':
                enhancer = ImageEnhance.Brightness(image)
                factor = random.uniform(0.8, 1.2)
                return enhancer.enhance(factor)
            elif augmentation_type == 'contrast':
                enhancer = ImageEnhance.Contrast(image)
                factor = random.uniform(0.8, 1.2)
                return enhancer.enhance(factor)
            else:
                logger.warning(f"Unknown augmentation type: {augmentation_type}")
                return image
        except Exception as e:
            logger.error(f"Error applying augmentation {augmentation_type}: {e}")
            return image

    def export_dataset(self, dataset_splits: Dict[str, List[Dict[str, Any]]]):
        """
        Export the dataset splits and store metadata in Metaforge.

        Args:
            dataset_splits (Dict[str, List[Dict[str, Any]]]): Dataset splits.
        """
        try:
            for split_name, data in dataset_splits.items():
                split_path = Path(self.config['output_folder']) / split_name
                split_path.mkdir(parents=True, exist_ok=True)
                metadata_file = split_path / 'metadata.json'

                # Save images and update metadata paths
                for item in data:
                    original_path = Path(item['Filepath'])
                    destination = split_path / original_path.name
                    if not destination.exists():
                        original_path.replace(destination)
                    item['Filepath'] = str(destination)

                # Save metadata
                with open(metadata_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Store metadata in Metaforge
                dataset_metadata = DatasetMetadataSchema(
                    dataset_split=split_name,
                    dataset_path=str(split_path),
                    total_images=len(data),
                    label_distribution=self._calculate_label_distribution(data),
                    processing_steps=['Export']
                )
                self.metaforge.add_dataset_metadata(dataset_metadata)

                logger.info(f"Exported dataset split '{split_name}' with {len(data)} images.")
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            raise

    def _calculate_label_distribution(self, data: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Calculate label distribution for a dataset split.

        Args:
            data (List[Dict[str, Any]]): List of image metadata dictionaries.

        Returns:
            Dict[int, int]: Label distribution.
        """
        distribution = {}
        for item in data:
            label = item.get('Label', -1)
            distribution[label] = distribution.get(label, 0) + 1
        return distribution

    def close(self):
        """
        Close the Metaforge database connection.
        """
        self.metaforge.close_connection()
        logger.debug("MuseDatasetManager connection closed.")
