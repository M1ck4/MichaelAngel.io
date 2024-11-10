# Changelog

All notable changes to this project will be documented in this file.

### [2.0.1] - 2024-11-11

#### Added
- **Database Integration:** SQL support added to maintain metadata for all extracted frames, providing a unified view of image data across tools.
- **JSONL and SQL Storage:** Writes metadata to both JSONL files for local storage and SQL database for centralized access.

#### Changed
- **Metadata Handling:** Adjusted to support dual storage of metadata in JSONL and SQL, facilitating enhanced tracking and attribution throughout the workflow.

### [2.0.0] - 2024-11-09

#### Added
- Expanded configuration management through YAML.
- Support for multithreaded frame extraction using `ThreadPoolExecutor` for improved performance.
- GPU acceleration option for frame extraction if CUDA is available.
- Customizable metadata fields expanded.
- Email notification customization with body templates and subject lines.
- Error handling options for saving error reports and managing existing directories.
- Progress bar using `tqdm` for frame extraction and processing.
- Command-line option `--image-format` to specify multiple output image formats (jpg, png, bmp, tiff).
- Logging enhancements with console output and customizable log levels.

#### Removed
- Removed hardcoded settings; all configurations are now managed via `config.yaml`.
- Deprecated legacy functions related to configuration management.

#### Changed
- Refactored argument parsing to accommodate new configuration options and clearer usage examples.
- Updated frame extraction logic to separate functions for sequential and multithreaded processing.
- Improved directory management logic for handling existing directories with user prompts.
- Enhanced metadata storage to support both YAML and JSON formats based on user preference.
- Centralized logging configuration for easy adjustments based on user-defined settings.

### [1.2.0] - 2024-10-23

#### Added
- Progress bar using `tqdm` to display operation progress.
- Command-line option `--image-format` to specify output image formats (jpg, png, bmp, tiff).
- Added `tqdm` to `requirements.txt`.

#### Removed
- Removed standard library modules (`argparse`, `logging`, `smtplib`, `email`) from `requirements.txt`.

#### Changed
- Updated frame saving logic to accommodate different image formats.

### [1.1.0] - 2024-10-23

#### Added
- Command-line arguments for email settings (`--email`, `--smtp-server`, etc.).
- SMTP authentication support in the email notification feature.

#### Changed
- Interval handling now uses time in seconds instead of frame counts.
- Improved error handling with detailed messages.
- Optimized performance by processing frames one at a time using a generator function.

#### Fixed
- Included the `__main__` block to ensure the script runs correctly when executed.

### [1.0.0] - 2024-10-08

#### Added
- Initial release.
