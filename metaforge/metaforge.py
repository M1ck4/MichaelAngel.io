import sqlite3
import json
from datetime import datetime
from models import ImageMetadata, ProcessingStep
from typing import Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Metaforge:
    def __init__(self, db_path: str = 'metaforge/metadata.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        logger.debug(f'Database connected at {db_path}')

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                source_api TEXT,
                download_info TEXT,
                attribution TEXT,
                processing_steps TEXT,
                additional_metadata TEXT,
                lineage TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        self.conn.commit()
        logger.debug('Database tables created or verified.')

    def add_image_metadata(self, metadata: ImageMetadata):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO images (
                image_id, source_api, download_info, attribution,
                processing_steps, additional_metadata, lineage,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.image_id,
            metadata.source_api,
            json.dumps(metadata.download_info),
            json.dumps(metadata.attribution),
            json.dumps([step.__dict__ for step in metadata.processing_steps]),
            json.dumps(metadata.additional_metadata),
            json.dumps(metadata.lineage),
            metadata.created_at.isoformat(),
            metadata.updated_at.isoformat()
        ))
        self.conn.commit()
        logger.debug(f'Metadata for image {metadata.image_id} added/updated.')

    def get_image_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM images WHERE image_id = ?', (image_id,))
        row = cursor.fetchone()
        if row:
            return ImageMetadata(
                image_id=row[0],
                source_api=row[1],
                download_info=json.loads(row[2]),
                attribution=json.loads(row[3]),
                processing_steps=[ProcessingStep(**step) for step in json.loads(row[4])],
                additional_metadata=json.loads(row[5]),
                lineage=json.loads(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8])
            )
        logger.warning(f'Metadata for image {image_id} not found.')
        return None

    def update_image_metadata(self, metadata: ImageMetadata):
        self.add_image_metadata(metadata)  # Reuse add_image_metadata for insert/update
        logger.debug(f'Metadata for image {metadata.image_id} updated.')

    def get_all_metadata(self) -> List[ImageMetadata]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM images')
        rows = cursor.fetchall()
        return [
            ImageMetadata(
                image_id=row[0],
                source_api=row[1],
                download_info=json.loads(row[2]),
                attribution=json.loads(row[3]),
                processing_steps=[ProcessingStep(**step) for step in json.loads(row[4])],
                additional_metadata=json.loads(row[5]),
                lineage=json.loads(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8])
            )
            for row in rows
        ]

    def export_metadata(self, export_formats: List[str], export_dir: str = 'metaforge/exports'):
        import os
        from utils import export_metadata_to_json, export_metadata_to_yaml

        os.makedirs(export_dir, exist_ok=True)
        metadata_list = self.get_all_metadata()

        if 'json' in export_formats:
            export_metadata_to_json(metadata_list, os.path.join(export_dir, 'metadata.json'))
            logger.info('Metadata exported to JSON.')

        if 'yaml' in export_formats:
            export_metadata_to_yaml(metadata_list, os.path.join(export_dir, 'metadata.yaml'))
            logger.info('Metadata exported to YAML.')

    def close_connection(self):
        self.conn.close()
        logger.debug('Database connection closed.')
