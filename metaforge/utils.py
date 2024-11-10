import json
import yaml
from typing import List
from models import ImageMetadata

def export_metadata_to_json(metadata_list: List[ImageMetadata], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([metadata.__dict__ for metadata in metadata_list], f, indent=2, default=str)

def export_metadata_to_yaml(metadata_list: List[ImageMetadata], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump([metadata.__dict__ for metadata in metadata_list], f)
