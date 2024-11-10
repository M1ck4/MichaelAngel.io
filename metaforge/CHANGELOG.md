# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2024-11-11

### Added

- **Configuration File (`config.yaml`)**: Added a configuration file for Metaforge, allowing customizable settings for:
  - Database connection
  - Metadata export options (formats and export directory)
  - Logging configuration (log level, log file path, and log message format)
  - Error handling settings (save error reports and specify report directory)

- **Enhanced `metadata_manager.py`**:
  - Integrated `config.yaml` support in `metadata_manager.py` to allow configurable database URL, logging, and metadata export settings.
  - `metadata_manager.py` now defaults to configuration values from `config.yaml` if provided; otherwise, it uses default settings.
  - Added error handling to log configuration loading issues, enhancing reliability.

- **Film Frame Metadata Management**:
  - Added support for managing film frame metadata via `FilmFrameMetadata` and associated methods.
  - Expanded metadata export functionality to handle film frame metadata, supporting multi-format export (JSON and YAML).

### Changed

- Updated `__init__.py` in Metaforge to include all essential components, aligning with the expanded functionality.
- Improved documentation within `metadata_manager.py` to reflect configurable options and ease of setup with `config.yaml`.

---

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
- Compliance management for tracking Creative Commons and other licenses across the AI pipeline.
