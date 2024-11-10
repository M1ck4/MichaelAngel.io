from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, List
from datetime import datetime
import json
import yaml
import os

from metaforge.models import Base, ImageMetadata, ImageProcessingMetadata, DatasetMetadata, FilmFrameMetadata
from metaforge.schemas import ImageMetadataSchema, ImageProcessingMetadataSchema, DatasetMetadataSchema, FilmFrameMetadataSchema


class Metaforge:
    def __init__(self, db_url: str = 'sqlite:///metaforge.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
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
            session.merge(db_metadata)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_image_metadata(self, image_id: str) -> Optional[ImageMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(ImageMetadata).filter(ImageMetadata.image_id == image_id).first()
            if db_metadata:
                return ImageMetadataSchema(
                    image_id=db_metadata.image_id,
                    source_api=db_metadata.source_api,
                    download_info=db_metadata.download_info,
                    attribution=db_metadata.attribution,
                    additional_metadata=db_metadata.additional_metadata,
                    lineage=db_metadata.lineage,
                    file_metadata=db_metadata.file_metadata
                )
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
            session.merge(db_metadata)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_image_processing_metadata(self, image_id: str) -> Optional[ImageProcessingMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(ImageProcessingMetadata).filter(ImageProcessingMetadata.image_id == image_id).first()
            if db_metadata:
                return ImageProcessingMetadataSchema(
                    image_id=db_metadata.image_id,
                    source_image_path=db_metadata.source_image_path,
                    processed_image_path=db_metadata.processed_image_path,
                    download_timestamp=db_metadata.download_timestamp,
                    processing_steps=db_metadata.processing_steps,
                    attribution=db_metadata.attribution,
                    extracted_metadata=db_metadata.extracted_metadata
                )
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
            session.add(db_metadata)
            session.commit()
        except Exception as e:
            session.rollback()
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
                return DatasetMetadataSchema(
                    dataset_split=db_metadata.dataset_split,
                    dataset_path=db_metadata.dataset_path,
                    total_images=db_metadata.total_images,
                    label_distribution=db_metadata.label_distribution,
                    processing_steps=db_metadata.processing_steps
                )
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
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_film_frame_metadata(self, frame_id: str) -> Optional[FilmFrameMetadataSchema]:
        session = self.Session()
        try:
            db_metadata = session.query(FilmFrameMetadata).filter(FilmFrameMetadata.frame_id == frame_id).first()
            if db_metadata:
                return FilmFrameMetadataSchema(
                    frame_id=db_metadata.frame_id,
                    film_id=db_metadata.film_id,
                    frame_number=db_metadata.frame_number,
                    timestamp=db_metadata.timestamp,
                    resolution=db_metadata.resolution,
                    processing_steps=db_metadata.processing_steps,
                    extracted_metadata=db_metadata.extracted_metadata
                )
            return None
        finally:
            session.close()
    
    # Export Metadata
    def export_metadata(self, formats: List[str], export_dir: str):
        os.makedirs(export_dir, exist_ok=True)
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
                for fmt in formats:
                    file_path = os.path.join(export_dir, f"{metadata.image_id}_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            
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
                for fmt in formats:
                    file_path = os.path.join(export_dir, f"{metadata.image_id}_processing_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
            
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
                for fmt in formats:
                    file_path = os.path.join(export_dir, f"{metadata.dataset_split}_dataset_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)

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
                for fmt in formats:
                    file_path = os.path.join(export_dir, f"{metadata.frame_id}_film_frame_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            yaml.dump(data, f)
        finally:
            session.close()
    
    # Close Database Connection
    def close_connection(self):
        self.engine.dispose()
