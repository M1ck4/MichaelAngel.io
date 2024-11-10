# modules/__init__.py

from .metadata_manager import MetadataManager
from .models import ImageMetadata
from .chisel import process_with_chisel
from .curator import process_with_curator
from .filmframe import process_with_filmframe
from .muse import process_with_muse
from .scribe import integrate_with_scribe

__all__ = [
    'MetadataManager',
    'ImageMetadata',
    'process_with_chisel',
    'process_with_curator',
    'process_with_filmframe',
    'process_with_muse',
    'integrate_with_scribe'
]
