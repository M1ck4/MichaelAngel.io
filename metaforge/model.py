from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ProcessingStep:
    step: str
    details: str
    timestamp: datetime

@dataclass
class ImageMetadata:
    image_id: str
    source_api: str
    download_info: Dict[str, Any]
    attribution: Dict[str, Any]
    processing_steps: List[ProcessingStep] = field(default_factory=list)
    additional_metadata: Dict[str, Any] = field(default_factory=dict)
    lineage: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
