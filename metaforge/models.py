# metaforge/models.py

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ImageMetadata(Base):
    __tablename__ = 'image_metadata'

    image_id = Column(String, primary_key=True, index=True)
    source_api = Column(String, nullable=False)
    download_info = Column(JSON, nullable=False)
    attribution = Column(JSON, nullable=False)
    additional_metadata = Column(JSON, nullable=True)
    lineage = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    file_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ImageMetadata(image_id={self.image_id}, source_api={self.source_api})>"
