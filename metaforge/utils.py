# metaforge/utils.py

import json
import yaml
from typing import Any


def serialize_json(data: Any, file_path: str):
    """Serialize data to JSON and save to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def serialize_yaml(data: Any, file_path: str):
    """Serialize data to YAML and save to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def deserialize_json(file_path: str) -> Any:
    """Deserialize JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def deserialize_yaml(file_path: str) -> Any:
    """Deserialize YAML data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
