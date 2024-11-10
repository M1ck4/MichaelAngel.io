# metaforge/metadata_manager.py

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import json

Base = declarative_base()

class ImageProcessingMetadata(Base):
    __tablename__ = 'image_processing_metadata'
    image_id = Column(String, primary_key=True, index=True)
    source_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=False)
    download_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_steps = Column(JSON, nullable=False)
    attribution = Column(JSON, nullable=False)
    extracted_metadata = Column(JSON, nullable=False)

class Metaforge:
    def __init__(self, db_url: str = 'sqlite:///metaforge.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def add_image_processing_metadata(self, metadata: 'ImageProcessingMetadataSchema'):
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
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_image_processing_metadata(self, image_id: str) -> Optional['ImageProcessingMetadataSchema']:
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
    
    def export_metadata(self, formats: List[str], export_dir: str):
        import os
        os.makedirs(export_dir, exist_ok=True)
        session = self.Session()
        try:
            all_metadata = session.query(ImageProcessingMetadata).all()
            for metadata in all_metadata:
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
                    file_path = os.path.join(export_dir, f"{metadata.image_id}_metadata.{fmt}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if fmt == 'json':
                            json.dump(data, f, indent=2)
                        elif fmt == 'yaml':
                            import yaml
                            yaml.dump(data, f)
        finally:
            session.close()
    
    def close_connection(self):
        self.engine.dispose()
