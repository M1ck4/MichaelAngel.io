from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ImageMetadata(Base):
    __tablename__ = 'image_metadata'
    image_id = Column(String, primary_key=True, index=True)
    source_api = Column(String, nullable=False)
    download_info = Column(JSON, nullable=False)
    attribution = Column(JSON, nullable=False)
    additional_metadata = Column(JSON, nullable=False)
    lineage = Column(JSON, nullable=False)
    file_metadata = Column(JSON, nullable=False)


class ImageProcessingMetadata(Base):
    __tablename__ = 'image_processing_metadata'
    image_id = Column(String, primary_key=True, index=True)  # Using image_id as primary key
    source_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=False)
    download_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_steps = Column(JSON, nullable=False)
    attribution = Column(JSON, nullable=False)
    extracted_metadata = Column(JSON, nullable=False)


class DatasetMetadata(Base):
    __tablename__ = 'dataset_metadata'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_split = Column(String, nullable=False)  # train, val, test
    dataset_path = Column(String, nullable=False)
    total_images = Column(Integer, nullable=False)
    label_distribution = Column(JSON, nullable=False)
    processing_steps = Column(JSON, nullable=False)

class FilmFrameMetadata(Base):
    __tablename__ = 'film_frame_metadata'
    frame_id = Column(String, primary_key=True, index=True)  # Unique identifier for each frame
    film_id = Column(String, nullable=False, index=True)  # Identifier for the film or video source
    frame_number = Column(Integer, nullable=False)  # Frame number within the film
    timestamp = Column(DateTime, nullable=True)  # Timestamp of the frame in the video
    resolution = Column(JSON, nullable=False)  # Resolution as { "width": int, "height": int }
    processing_steps = Column(JSON, nullable=False)  # Steps applied to the frame
    extracted_metadata = Column(JSON, nullable=True)  # Additional metadata extracted from the frame
