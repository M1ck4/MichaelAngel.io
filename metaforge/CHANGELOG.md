# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-11-11

### Added

- Initial release of Metaforge as the database and metadata management tool for the MichaelAngel.io Framework.
- Core components and files:
  - **metadata_manager.py**: Main script for managing metadata operations.
  - **models.py**: Database models defining the structure of stored metadata.
  - **schemas.py**: Data validation schemas for consistent metadata structure.
  - **utils.py**: Utility functions to support metadata operations and database management.
  - **requirements.txt**: Dependencies required to run Metaforge.
- Support for CRUD (Create, Read, Update, Delete) operations for metadata entries.
- Initial configuration setup with `config.yaml` for database settings, logging levels, and other options.
- Compliance management for tracking Creative Commons and other licenses across the AI pipeline.
