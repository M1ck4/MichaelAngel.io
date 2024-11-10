import os
import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, List
from datetime import datetime

from metaforge.models import (
    Base,
    ImageMetadata,
    ImageProcessingMetadata,
    DatasetMetadata,
    FilmFrameMetadata
)
from metaforge.schemas import (
    ImageMetadataSchema,
    ImageProcessingMetadataSchema,
    DatasetMetadataSchema,
    FilmFrameMetadataSchema
)
import logging

# Load configuration settings
def load_config(config_file="config.yaml"):
    default_config = {
        'database': {
            'url': 'sqlite:///metaforge.db'
        },
        'metadata_export': {
            'export_dir': 'metaforge/exports',
            'formats': ['json', 'yaml']
        },
        'logging': {
            'level': 'INFO',
            'log_file': 'metaforge.log',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'error_handling': {
            'save_error_report': True,
            'error_report_path': 'metaforge/error_reports/'
        }
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
                # Update default_config recursively
                def update_dict(d, u):
                    for k, v in u.items():
                        if isinstance(v, dict):
                            d[k] = update_dict(d.get(k, {}), v)
                        else:
                            d[k] = v
                    return d
                update_dict(default_config, yaml_config)
        except yaml.YAMLError as e:
            print(f"Error parsing the configuration file: {e}")
            # Continue with default configuration
    else:
        print(f"Configuration file '{config_file}' not found. Using default settings.")

    return default_config

# Configure logging
def setup_logging(log_config):
    log_level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    log_file = log_config.get('log_file', 'metaforge.log')
    log_format = log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')

    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format=log_format
    )
    # Also output to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger('').addHandler(console_handler)

class Metaforge:
    def __init__(self, config: dict = None, config_file: str = "config.yaml"):
        if config is None:
            config = load_config(config_file)

        # Setup logging
        setup_logging(config.get('logging', {}))
        self.logger = logging.getLogger(__name__)

        # Database setup
        db_url = config['database'].get('url', 'sqlite:///metaforge.db')
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Metadata export settings
        self.export_dir = config['metadata_export'].get('export_dir', 'metaforge/exports')
        self.export_formats = config['metadata_export'].get('formats', ['json', 'yaml'])

        # Error handling settings
        self.error_handling = config.get('error_handling', {})
        if self.error_handling.get('save_error_report', True):
            os.makedirs(self.error_handling.get('error_report_path', 'metaforge/error_reports/'), exist_ok=True)

    # Image Metadata Management
    def add_image_metadata(self, metadata: ImageMetadataSchema):
        session = self.Session()
        try:
            db_metadata = ImageMetadata(
                image_id=metadata.image_id,
                source_api=metadata.source_api,
                download_info=metadata.download_info,
                attribution=metadata.attribution,
                additional_metadata=metadata.additional_metadata,
                lineage=metadata.lineage,
                file_metadata=metadata.file_metadata
            )
            session.merge(db_metadata)  # Use merge to handle existing records
            session.commit()
            self.logger.info(f"Image metadata added for image_id: {metadata.image_id}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding image metadata for image_id {metadata.image_id}: {e}")
            if self.error_handling.get('save_error_report', True):
                self.save_error_report(e)
            raise e
        finally:
            session.close()

    def get_image_metadata(self, image_id: str) -> Optional[ImageMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(ImageMetadata).filter(ImageMetadata.image_id == image_id).first()
            if db_metadata:
                self.logger.info(f"Retrieved image metadata for image_id: {image_id}")
                return ImageMetadataSchema(
                    image_id=db_metadata.image_id,
                    source_api=db_metadata.source_api,
                    download_info=db_metadata.download_info,
                    attribution=db_metadata.attribution,
                    additional_metadata=db_metadata.additional_metadata,
                    lineage=db_metadata.lineage,
                    file_metadata=db_metadata.file_metadata
                )
            self.logger.warning(f"No image metadata found for image_id: {image_id}")
            return None
        finally:
            session.close()

    # Image Processing Metadata Management
    def add_image_processing_metadata(self, metadata: ImageProcessingMetadataSchema):
        session = self.Session()
        try:
            db_metadata = ImageProcessingMetadata(
                image_id=metadata.image_id,
                source_image_path=metadata.source_image_path,
                processed_image_path=metadata.processed_image_path,
                download_timestamp=metadata.download_timestamp,
                processing_steps=metadata.processing_steps,
                attribution=metadata.attribution,
                extracted_metadata=metadata.extracted_metadata
            )
            session.merge(db_metadata)  # Use merge to handle existing records
            session.commit()
            self.logger.info(f"Image processing metadata added for image_id: {metadata.image_id}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding image processing metadata for image_id {metadata.image_id}: {e}")
            if self.error_handling.get('save_error_report', True):
                self.save_error_report(e)
            raise e
        finally:
            session.close()

    def get_image_processing_metadata(self, image_id: str) -> Optional[ImageProcessingMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(ImageProcessingMetadata).filter(ImageProcessingMetadata.image_id == image_id).first()
            if db_metadata:
                self.logger.info(f"Retrieved image processing metadata for image_id: {image_id}")
                return ImageProcessingMetadataSchema(
                    image_id=db_metadata.image_id,
                    source_image_path=db_metadata.source_image_path,
                    processed_image_path=db_metadata.processed_image_path,
                    download_timestamp=db_metadata.download_timestamp,
                    processing_steps=db_metadata.processing_steps,
                    attribution=db_metadata.attribution,
                    extracted_metadata=db_metadata.extracted_metadata
                )
            self.logger.warning(f"No image processing metadata found for image_id: {image_id}")
            return None
        finally:
            session.close()

    # Dataset Metadata Management
    def add_dataset_metadata(self, metadata: DatasetMetadataSchema):
        session = self.Session()
        try:
            db_metadata = DatasetMetadata(
                dataset_split=metadata.dataset_split,
                dataset_path=metadata.dataset_path,
                total_images=metadata.total_images,
                label_distribution=metadata.label_distribution,
                processing_steps=metadata.processing_steps
            )
            session.merge(db_metadata)
            session.commit()
            self.logger.info(f"Dataset metadata added for dataset_split: {metadata.dataset_split}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding dataset metadata for dataset_split {metadata.dataset_split}: {e}")
            if self.error_handling.get('save_error_report', True):
                self.save_error_report(e)
            raise e
        finally:
            session.close()

    def get_dataset_metadata(self, dataset_split: str, dataset_path: str) -> Optional[DatasetMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(DatasetMetadata).filter(
                DatasetMetadata.dataset_split == dataset_split,
                DatasetMetadata.dataset_path == dataset_path
            ).first()
            if db_metadata:
                self.logger.info(f"Retrieved dataset metadata for split: {dataset_split}")
                return DatasetMetadataSchema(
                    dataset_split=db_metadata.dataset_split,
                    dataset_path=db_metadata.dataset_path,
                    total_images=db_metadata.total_images,
                    label_distribution=db_metadata.label_distribution,
                    processing_steps=db_metadata.processing_steps
                )
            self.logger.warning(f"No dataset metadata found for split: {dataset_split}")
            return None
        finally:
            session.close()

    # Film Frame Metadata Management
    def add_film_frame_metadata(self, metadata: FilmFrameMetadataSchema):
        session = self.Session()
        try:
            db_metadata = FilmFrameMetadata(
                frame_id=metadata.frame_id,
                film_id=metadata.film_id,
                frame_number=metadata.frame_number,
                timestamp=metadata.timestamp,
                resolution=metadata.resolution,
                processing_steps=metadata.processing_steps,
                extracted_metadata=metadata.extracted_metadata
            )
            session.merge(db_metadata)
            session.commit()
            self.logger.info(f"Film frame metadata added for frame_id: {metadata.frame_id}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding film frame metadata for frame_id {metadata.frame_id}: {e}")
            if self.error_handling.get('save_error_report', True):
                self.save_error_report(e)
            raise e
        finally:
            session.close()

    def get_film_frame_metadata(self, frame_id: str) -> Optional[FilmFrameMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(FilmFrameMetadata).filter(FilmFrameMetadata.frame_id == frame_id).first()
            if db_metadata:
                self.logger.info(f"Retrieved film frame metadata for frame_id: {frame_id}")
                return FilmFrameMetadataSchema(
                    frame_id=db_metadata.frame_id,
                    film_id=db_metadata.film_id,
                    frame_number=db_metadata.frame_number,
                    timestamp=db_metadata.timestamp,
                    resolution=db_metadata.resolution,
                    processing_steps=db_metadata.processing_steps,
                    extracted_metadata=db_metadata.extracted_metadata
                )
            self.logger.warning(f"No film frame metadata found for frame_id: {frame_id}")
            return None
        finally:
            session.close()

    # Export Metadata
    def export_metadata(self):
        os.makedirs(self.export_dir, exist_ok=True)
        session = self.Session()
        try:
            # Export Image Metadata
            all_image_metadata = session.query(ImageMetadata).all()
            for metadata in all_image_metadata:
                data = {
                    'image_id': metadata.image_id,
                    'source_api': metadata.source_api,
                    'download_info': metadata.download_info,
                    'attribution': metadata.attribution,
                    'additional_metadata': metadata.additional_metadata,
                    'lineage': metadata.lineage,
                    'file_metadata': metadata.file_metadata
                }
                for fmt in self.export_formats:
                    file_path = os.path.join(self.export_dir, f"{metadata.image_id}_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            self.logger.info("Image metadata exported successfully.")

            # Export Image Processing Metadata
            all_processing_metadata = session.query(ImageProcessingMetadata).all()
            for metadata in all_processing_metadata:
                data = {
                    'image_id': metadata.image_id,
                    'source_image_path': metadata.source_image_path,
                    'processed_image_path': metadata.processed_image_path,
                    'download_timestamp': metadata.download_timestamp.isoformat(),
                    'processing_steps': metadata.processing_steps,
                    'attribution': metadata.attribution,
                    'extracted_metadata': metadata.extracted_metadata
                }
                for fmt in self.export_formats:
                    file_path = os.path.join(self.export_dir, f"{metadata.image_id}_processing_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            self.logger.info("Image processing metadata exported successfully.")

            # Export Dataset Metadata
            all_dataset_metadata = session.query(DatasetMetadata).all()
            for metadata in all_dataset_metadata:
                data = {
                    'dataset_split': metadata.dataset_split,
                    'dataset_path': metadata.dataset_path,
                    'total_images': metadata.total_images,
                    'label_distribution': metadata.label_distribution,
                    'processing_steps': metadata.processing_steps
                }
                for fmt in self.export_formats:
                    file_path = os.path.join(self.export_dir, f"{metadata.dataset_split}_dataset_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            self.logger.info("Dataset metadata exported successfully.")

            # Export Film Frame Metadata
            all_film_frame_metadata = session.query(FilmFrameMetadata).all()
            for metadata in all_film_frame_metadata:
                data = {
                    'frame_id': metadata.frame_id,
                    'film_id': metadata.film_id,
                    'frame_number': metadata.frame_number,
                    'timestamp': metadata.timestamp.isoformat(),
                    'resolution': metadata.resolution,
                    'processing_steps': metadata.processing_steps,
                    'extracted_metadata': metadata.extracted_metadata
                }
                for fmt in self.export_formats:
                    file_path = os.path.join(self.export_dir, f"{metadata.frame_id}_film_frame_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            self.logger.info("Film frame metadata exported successfully.")
        except Exception as e:
            self.logger.error(f"Error exporting metadata: {e}")
            if self.error_handling.get('save_error_report', True):
                self.save_error_report(e)
            raise e
        finally:
            session.close()

    def save_error_report(self, error):
        error_report_path = self.error_handling.get('error_report_path', 'metaforge/error_reports/')
        os.makedirs(error_report_path, exist_ok=True)
        error_file = os.path.join(error_report_path, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(error_file, 'w') as f:
            f.write(str(error))
        self.logger.info(f"Error report saved to {error_file}")

    # Close Database Connection
    def close_connection(self):
        self.engine.dispose()
        self.logger.info("Database connection closed.")
