# metaforge/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ImageProcessingMetadataSchema(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the image")
    source_image_path: str = Field(..., description="Path to the original downloaded image")
    processed_image_path: str = Field(..., description="Path to the processed image")
    download_timestamp: datetime = Field(..., description="Timestamp when the image was downloaded")
    processing_steps: List[Dict] = Field(default_factory=list, description="List of processing steps applied to the image")
    attribution: Dict = Field(default_factory=dict, description="Attribution information for the image")
    extracted_metadata: Dict = Field(default_factory=dict, description="Extracted metadata from the image")
