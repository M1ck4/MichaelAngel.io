
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class DownloadInfo(BaseModel):
    url: str
    download_timestamp: datetime
    download_status: str

class Attribution(BaseModel):
    author: str
    license: str
    source_url: str

class ImageMetadataSchema(BaseModel):
    image_id: str
    source_api: str
    download_info: DownloadInfo
    attribution: Attribution
    additional_metadata: Optional[Dict[str, Any]] = None
    lineage: Optional[List[str]] = None
    file_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

