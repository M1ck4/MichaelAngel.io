# metaforge/utils.py

import yaml
import json
from typing import Any, Dict

def export_metadata_to_json(metadata: Dict[str, Any], export_dir: str):
    for image_id, data in metadata.items():
        file_path = f"{export_dir}/{image_id}_metadata.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data.dict(), f, indent=2)

def export_metadata_to_yaml(metadata: Dict[str, Any], export_dir: str):
    for image_id, data in metadata.items():
        file_path = f"{export_dir}/{image_id}_metadata.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data.dict(), f)
