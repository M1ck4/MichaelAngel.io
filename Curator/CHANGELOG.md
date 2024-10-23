Changelog

All notable changes to this project will be documented in this file.

[1.2.0] - 2024-10-23

Added

  Global Metadata File: Introduced global_metadata.json to track all downloaded images across runs and avoid duplicates.
  Per-Category Metadata Files: Maintained metadata.json files within each category folder for individual image metadata.
  File Extension Fix: Corrected file extension extraction using urllib.parse.urlparse and os.path.splitext.
  Progress Bar: Implemented tqdm progress bars to display download progress for each API and search term.
  Email Notifications: Added the --email command-line option and email notification feature with a summary of download metrics.
  Custom Rate Limiter: Developed a SimpleRateLimiter class to handle API rate limits based on configurations.
  Detailed Logging: Enhanced logging messages for better traceability and debugging.

Changed

  Logging Configuration: Updated to use the log_directory specified in config.yaml.
  Duplicate Checking: Modified image download logic to check against global_metadata.json before downloading to prevent duplicates.
  Pagination Support: Implemented pagination to fetch additional pages of images until the desired number is downloaded or no more images are available.
  Code Refactoring: Refactored code into modular functions for improved readability and maintainability.
  Error Handling: Improved exception handling for API calls and image downloads, including retries and graceful degradation.

Fixed

  Image Extension Issue: Resolved an issue where images were saved with incorrect file extensions (e.g., .3), ensuring images are saved with valid extensions and are viewable.

[1.1.0] - 2024-10-15

Added

  Configuration File Support: Implemented config.yaml to allow dynamic settings for API keys, rate limits, search terms, email settings, maximum images per term, and log directory.
  Command-Line Argument: Added the --config option to specify the path to the configuration file.
  Metrics Collection: Enhanced metrics collection for total images downloaded, images per category, total requests made, successful and failed requests, API times, and retries.
  Email Settings in Config: Included email settings in config.yaml for notifications.
  Custom Rate Limiter: Introduced a rate limiter to handle API rate limits per the configuration.

Changed

  Removed Hardcoded Values: Replaced hardcoded settings with configurations loaded from config.yaml.
  Logging Setup: Moved logging setup after configuration loading to apply the settings from the config file.
  Logging Enhancements: Improved log messages for better traceability.
  Error Handling: Enhanced exception handling during API calls and image downloads to manage timeouts, connection errors, and HTTP errors gracefully.

Fixed

  Dependency Management: Ensured all necessary modules are imported and specified in requirements.

[1.0.0] - 2024-10-08

  Initial Release: Basic script to download images from various APIs (Pixabay, Unsplash, Pexels, Flickr, Google CSE) using predefined search terms.
  Per-Category Downloads: Saved images into category-specific folders based on search terms.
  Metadata Storage: Stored metadata for each image in per-category metadata.json files.
  Basic Logging: Included basic logging and error handling mechanisms.
