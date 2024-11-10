from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class ImageMetadataSchema(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the image")
    source_api: str = Field(..., description="API or source from where the image was obtained")
    download_info: Dict[str, Any] = Field(..., description="Information related to the image download")
    attribution: Dict[str, Any] = Field(..., description="Attribution details for the image")
    additional_metadata: Dict[str, Any] = Field(..., description="Any additional metadata related to the image")
    lineage: Dict[str, Any] = Field(..., description="Lineage information of the image processing")
    file_metadata: Dict[str, Any] = Field(..., description="Metadata related to the image file")


class ImageProcessingMetadataSchema(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the image")
    source_image_path: str = Field(..., description="Path to the original image")
    processed_image_path: str = Field(..., description="Path to the processed image")
    download_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the image was downloaded")
    processing_steps: List[str] = Field(..., description="List of processing steps applied to the image")
    attribution: Dict[str, Any] = Field(..., description="Attribution details for the image")
    extracted_metadata: Dict[str, Any] = Field(..., description="Extracted metadata from the image")


class DatasetMetadataSchema(BaseModel):
    dataset_split: str = Field(..., description="Name of the dataset split (train, val, test)")
    dataset_path: str = Field(..., description="Path to the dataset split directory")
    total_images: int = Field(..., description="Total number of images in the split")
    label_distribution: Dict[int, int] = Field(default_factory=dict, description="Distribution of labels in the split")
    processing_steps: List[str] = Field(default_factory=list, description="List of processing steps applied to the dataset")
