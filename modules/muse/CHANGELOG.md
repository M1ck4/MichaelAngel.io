# Changelog

All notable changes to this project will be documented in this file.

## Muse Changelog

All notable changes to Muse will be documented in this file.

### [1.0.1] - 2024-11-11

#### Added
- **Database Integration:** SQL support incorporated to track image metadata from preprocessing to dataset creation, allowing for efficient metadata queries and management.
- **JSONL and SQL Storage:** Stores metadata in both JSONL and SQL formats for flexible access.

#### Changed
- **Metadata Workflow:** Enhanced to support SQL integration, ensuring each image’s metadata is logged consistently from input to export stages.

### [1.0.0] - 2024-10-24

#### Added
- **Metadata Loading:**
  - Implemented `load_metadata` to aggregate metadata from multiple JSON files within the input directory.
  - Ensured absolute file paths are correctly assigned to each image based on metadata.

- **Quality Control:**
  - Added `quality_control` function to verify image formats and dimensions.
  - Configurable minimum image size and allowed formats through command-line arguments.

- **Dataset Splitting:**
  - Implemented `split_dataset` to divide data into training, validation, and test sets.
  - Added support for stratified splitting to maintain label distribution across splits.

- **Label Application:**
  - Developed `apply_labels` to assign numerical labels based on category information in metadata.
  - Configurable label mapping through the script.

- **Data Augmentation:**
  - Added advanced augmentation techniques: MixUp and CutMix.
  - Implemented `mixup_images` and `cutmix_images` functions for image blending and cropping.
  - Enabled multiprocessing in `augment_dataset` to accelerate augmentation processes.
  - Configurable augmentation types and multipliers via command-line arguments.

- **Multiprocessing:**
  - Integrated `multiprocessing` to enhance performance during data augmentation.
  - Utilized `tqdm` for progress bars to monitor augmentation and export processes.

- **Creative Commons Integration:**
  - Extracted and preserved Creative Commons data from metadata.
  - Ensured that attribution information is maintained throughout dataset processing.

- **Analytics & Monitoring:**
  - Implemented `analyze_dataset` to log dataset statistics, including total images and label distributions per split.
  - Enhanced logging to include processing steps and augmentation details for each image.

- **Export Functionality:**
  - Developed `export_dataset` to organize and save datasets into designated folders (`train`, `val`, `test`).
  - Preserved metadata with detailed processing steps for each image.

#### Changed
- **Script Structure:**
  - Refactored script for better readability and maintainability.
  - Separated augmentation logic to facilitate multiprocessing compatibility.

- **Metadata Handling:**
  - Improved metadata loading to include paths and attribution data from previous tools (`Curator`, `Chisel`, `FilmFrame`).

- **Augmentation Process:**
  - Enhanced unique naming for augmented images to prevent filename collisions.
  - Ensured all images are converted to RGB mode before processing to maintain consistency.

#### Fixed
- **Import Issues:**
  - Removed unused imports (`random`, `ImageOps`) to eliminate IDE warnings and optimize performance.

- **Quality Control Logic:**
  - Fixed issues with image quality checks to accurately filter out unsuitable images based on size and format.

- **Augmentation Errors:**
  - Resolved potential errors in MixUp and CutMix functions by ensuring additional images are correctly sampled and processed.
