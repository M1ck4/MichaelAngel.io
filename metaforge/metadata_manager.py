# metaforge/metadata_manager.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, ImageMetadata
from .schemas import ImageMetadataSchema
import logging

logger = logging.getLogger(__name__)

class Metaforge:
    def __init__(self, db_url: str = 'sqlite:///metaforge.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.debug(f'Database connected at {db_url}')

    def get_session(self) -> Session:
        return self.SessionLocal()

    def add_image_metadata(self, metadata: ImageMetadataSchema):
        session = self.get_session()
        try:
            db_metadata = ImageMetadata(
                image_id=metadata.image_id,
                source_api=metadata.source_api,
                download_info=metadata.download_info.dict(),
                attribution=metadata.attribution.dict(),
                additional_metadata=metadata.additional_metadata,
                lineage=metadata.lineage,
                file_metadata=metadata.file_metadata
            )
            session.add(db_metadata)
            session.commit()
            session.refresh(db_metadata)
            logger.debug(f'Added metadata for image_id: {metadata.image_id}')
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f'Error adding metadata for image_id {metadata.image_id}: {e}')
        finally:
            session.close()

    def get_image_metadata(self, image_id: str) -> Optional[ImageMetadataSchema]:
        session = self.get_session()
        try:
            db_metadata = session.query(ImageMetadata).filter(ImageMetadata.image_id == image_id).first()
            if db_metadata:
                return ImageMetadataSchema.from_orm(db_metadata)
            return None
        except SQLAlchemyError as e:
            logger.error(f'Error retrieving metadata for image_id {image_id}: {e}')
            return None
        finally:
            session.close()

    def export_metadata(self, formats: List[str], export_dir: str):
        session = self.get_session()
        try:
            all_metadata = session.query(ImageMetadata).all()
            for db_metadata in all_metadata:
                metadata_schema = ImageMetadataSchema.from_orm(db_metadata)
                filename = f"{metadata_schema.image_id}_metadata"
                if 'json' in formats:
                    with open(f"{export_dir}/{filename}.json", 'w', encoding='utf-8') as f:
                        f.write(metadata_schema.json(indent=2))
                if 'yaml' in formats:
                    with open(f"{export_dir}/{filename}.yaml", 'w', encoding='utf-8') as f:
                        f.write(metadata_schema.json())  # You might want to convert to YAML properly
            logger.info(f'Metadata exported to {export_dir} in formats: {formats}')
        except SQLAlchemyError as e:
            logger.error(f'Error exporting metadata: {e}')
        finally:
            session.close()

    def close_connection(self):
        self.engine.dispose()
        logger.debug('Database connection closed.')
