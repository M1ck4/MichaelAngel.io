# curator/metadata_manager.py

import logging
from typing import Any, Dict
from metaforge import Metaforge, ImageMetadataSchema

logger = logging.getLogger(__name__)

class CuratorMetadataManager:
    def __init__(self, config: Dict[str, Any]):
        self.metaforge = Metaforge(db_url=config['database']['url'])
        logger.debug("CuratorMetadataManager initialized.")

    def add_image_metadata(self, metadata: Dict[str, Any]):
        """
        Add image metadata to Metaforge.

        Args:
            metadata (Dict[str, Any]): Metadata dictionary for the image.
        """
        try:
            metadata_schema = ImageMetadataSchema(**metadata)
            self.metaforge.add_image_metadata(metadata_schema)
            logger.info(f"Added metadata for image_id: {metadata['image_id']}")
        except Exception as e:
            logger.error(f"Failed to add metadata for image_id: {metadata.get('image_id', 'Unknown')}: {e}")
            raise

    def get_image_metadata(self, image_id: str) -> Dict[str, Any]:
        """
        Retrieve image metadata from Metaforge.

        Args:
            image_id (str): Unique identifier for the image.

        Returns:
            Dict[str, Any]: Metadata dictionary for the image.
        """
        try:
            metadata_schema = self.metaforge.get_image_metadata(image_id)
            if metadata_schema:
                logger.info(f"Retrieved metadata for image_id: {image_id}")
                return metadata_schema.dict()
            else:
                logger.warning(f"No metadata found for image_id: {image_id}")
                return {}
        except Exception as e:
            logger.error(f"Failed to retrieve metadata for image_id: {image_id}: {e}")
            raise
