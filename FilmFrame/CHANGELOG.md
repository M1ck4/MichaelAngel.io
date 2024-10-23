# Changelog

## [1.2.0] - 2024-10-23

### Added

- Progress bar using `tqdm` to display operation progress.
- Command-line option `--image-format` to specify output image formats (jpg, png, bmp, tiff).

### Changed

- Updated frame saving logic to accommodate different image formats.


All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-10-23

### Added

- Command-line arguments for email settings (`--email`, `--smtp-server`, etc.).
- SMTP authentication support in the email notification feature.

### Changed

- Interval handling now uses time in seconds instead of frame counts.
- Improved error handling with detailed messages.
- Optimized performance by processing frames one at a time using a generator function.

### Fixed

- Included the `__main__` block to ensure the script runs correctly when executed.

## [1.0.0] - YYYY-MM-DD

- Initial release.
