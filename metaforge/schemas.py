# metaforge/schemas.py

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class ProcessingStepSchema(BaseModel):
    step: str
    details: str
    timestamp: datetime

class ImageMetadataSchema(BaseModel):
    image_id: str
    source_api: str
    download_info: Dict[str, Any]
    attribution: Dict[str, Any]
    processing_steps: List[ProcessingStepSchema]
    additional_metadata: Dict[str, Any]
    lineage: List[str]
    created_at: datetime
    updated_at: datetime
