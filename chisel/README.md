# Chisel

Chisel is a powerful preprocessing tool designed to enhance image datasets by filtering out low-quality images and preparing them for AI training. It ensures that your dataset is both high-quality and ethically sound, streamlining the workflow for artists, developers, and researchers.
Table of Contents

## Overview

Chisel serves as the preprocessing powerhouse within the MichaelAngel.io pipeline. Its primary function is to filter out low-quality images and prepare them for AI training by performing the following tasks:

-    Quality Control: Removes duplicates and low-quality images based on size and blurriness.
-    Consistent Resizing: Ensures all images meet specified dimensions for uniformity.
-    Metadata Preservation: Retains essential metadata and attribution information.
-    Batch Processing: Efficiently handles large volumes of images using parallel processing.

By automating these critical preprocessing steps, Chisel ensures that your image datasets are clean, organized, and ready for AI-driven creative projects.

## Features

-    Automated Quality Checks: Filters images based on size and blurriness to maintain high dataset quality.
-    Metadata Extraction: Extracts and preserves EXIF metadata for comprehensive dataset information.
-    Duplicate Detection: Identifies and removes duplicate images using content hashing.
-    Image Enhancement: Enhances image properties such as brightness, contrast, color, and sharpness.
-    Flexible Output Formats: Supports saving processed images in JPEG, PNG, or NumPy array formats.
-    Efficient Processing: Utilizes parallel processing to handle large datasets swiftly.
-    Comprehensive Logging: Logs all preprocessing activities for transparency and troubleshooting.

## Installation

### Prerequisites

-    Python 3.8+
-    Git

### Clone the Repository

    git clone https://github.com/M1ck4/MichaelAngel.io.git

### Navigate to the Chisel Directory

    cd MichaelAngel.io/chisel

### Create a Virtual Environment (Optional but Recommended)

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

### Install Dependencies

Ensure you have pip installed, then run:

    pip install -r requirements.txt

If you encounter issues with specific packages, ensure you have the necessary system libraries installed, especially for opencv-python.

## Usage

Chisel can be executed via the command line with various arguments to customize its behavior.
Command-Line Arguments

    python Chisel.py --image_folder <input_folder> --output_folder <output_folder> [options]

### Required Arguments

-    image_folder: Path to the input folder containing images to be processed.
-    output_folder: Path to the output folder where processed images and metadata will be saved.

### Optional Arguments

-    target_size: Target size for image resizing in the format width height. Default is 256 256.
-    output_format: Output format for processed images. Choices are JPEG, PNG, numpy. Default is JPEG.
-    min_size: Minimum size (in pixels) for image quality. Images smaller than this will be excluded. Default is 128.
-    blur_threshold: Blur threshold for image quality check. Images with blurriness below this threshold will be excluded. Default is 100.0.
-    enhancement_factors: Enhancement factors for brightness, contrast, color, and sharpness in the format brightness contrast color sharpness. Default is 1.0 1.0 1.0 1.0.
-    quality: Quality for JPEG output (1-100). Default is 85.

## Example Usages

**Chisel** offers flexibility through various command-line arguments, allowing you to tailor the preprocessing pipeline to your specific needs. Below are several example usages, ranging from basic to complex scenarios.

---

### Process images using default settings.

    python Chisel.py --image_folder ./raw_images --output_folder ./processed_images

This command processes images from ./raw_images, resizes them to 512x512, saves them in PNG format, excludes images smaller than 150 pixels or with a blur variance below 
120.0, enhances brightness by 1.2, contrast by 1.1, color by 1.3, leaves sharpness unchanged, and sets JPEG quality to 90.

Description:
This command processes all images in the ./raw_images directory and saves the processed images and metadata to the ./processed_images directory using default settings:

-    Resizing: Images are resized to 256x256 pixels.
-    Output Format: JPEG.
-    Minimum Size: 128 pixels.
-    Blur Threshold: 100.0.
-    Enhancement Factors: Brightness, contrast, color, and sharpness are set to 1.0 (no change).
-    JPEG Quality: 85.

---

### Specifying Output Format

Save processed images in PNG format instead of the default JPEG.

    python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --output_format PNG

Description:
In addition to the basic processing, this command saves the processed images in PNG format, which is lossless and supports transparency.

-    Outful format: PNG

---

### Adjusting Image Size

Resize images to custom dimensions.

    python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --target_size 512 512

Description:
This command resizes all images to 512x512 pixels, allowing for larger images in the processed dataset.

-    Resizing: 512x512 pixels.

---

### Enhancing Image Properties

Enhance brightness and contrast of images.

    python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --enhancement_factors 1.2 1.1 1.0 1.0

Description:
This command adjusts the brightness and contrast of the images:

-    Brightness: Increased by a factor of 1.2.
-    Contrast: Increased by a factor of 1.1.
-    Color & Sharpness: Remain unchanged (1.0).

---

### Combining Multiple Options

Perform advanced preprocessing with custom settings.

    python Chisel.py \
      --image_folder ./raw_images \
      --output_folder ./processed_images \
      --target_size 512 512 \
      --output_format numpy \
      --min_size 150 \
      --blur_threshold 120.0 \
      --enhancement_factors 1.2 1.1 1.3 1.0 \
      --quality 90

Description:
This comprehensive command performs multiple preprocessing steps to ensure a high-quality and well-organized dataset:

-    Resizing: 512x512 pixels.
-    Output Format: NumPy arrays (numpy), suitable for AI training.
-    Minimum Size: Excludes images smaller than 150 pixels.
-    Blur Threshold: Excludes images with blur variance below 120.0.
Enhancements:
  -    Brightness: Increased by 1.2.
    -     Contrast: Increased by 1.1.
    -    Color: Increased by 1.3.
    -    Sharpness: Unchanged (1.0).
    -    JPEG Quality: 90 (applicable if output format is JPEG).

This combination ensures that only high-quality, well-enhanced images are included in the final dataset, saved in a format suitable for AI training.

## Configuration

Chisel provides flexibility through various command-line arguments, allowing you to tailor the preprocessing pipeline to your specific needs. Below is a breakdown of the key configurations:

### Image Quality Parameters:

-    Minimum Size (--min_size): Ensures that only images above a certain resolution are included.
-    Blur Threshold (--blur_threshold): Filters out blurry images based on variance in Laplacian.

 ### Image Enhancement Factors (--enhancement_factors):
 
-    Brightness: Adjusts the brightness level.
-    Contrast: Modifies the contrast of the image.
-    Color or: Alters the color saturation.
-    Sharpness: Changes the sharpness of the image.

### Output Settings:

-    Target Size (--target_size): Specifies the dimensions to which images will be resized.
-    Output Format (--output_format): Determines the format in which processed images are saved.
-    Quality (--quality): Sets the quality level for JPEG images.

## Logging

Chisel maintains a comprehensive log of all preprocessing activities to facilitate transparency and troubleshooting. The logs are saved in a file named preprocessing_log.txt located in the root directory of the Chisel project.
Log Contents

-    Timestamp: Records the date and time of each logged event.
-    Log Level: Indicates the severity of the event (INFO, WARNING, ERROR).
-    Message: Describes the event or issue encountered.

### Example Log Entries

yaml

    2024-04-27 12:34:56,789 - INFO - Starting preprocessing for images in ./raw_images
    2024-04-27 12:35:01,123 - INFO - Image ./raw_images/image1.jpg is too small.
    2024-04-27 12:35:05,456 - ERROR - Error processing ./raw_images/image2.jpg: [Errno 2] No such file or directory
    2024-04-27 12:35:10,789 - INFO - Successfully processed and saved ./raw_images/image3.jpg

### Contributing

We welcome contributions to enhance Chisel and make it even more robust and user-friendly. Whether you're fixing bugs, adding new features, or improving documentation, your efforts are highly appreciated!
How to Contribute

### Fork the Repository:
Click the "Fork" button at the top-right corner of the repository page to create a personal copy.

### Clone Your Fork:

    git clone https://github.com/<your-username>/MichaelAngel.io.git

### Create a New Branch:

    git checkout -b feature/your-feature-name

### Make Your Changes:

Implement your feature or bug fix in the chisel/Chisel.py file or update the README.md as needed.

### Commit Your Changes:

    git commit -m "Add feature: your feature description"

### Push to Your Fork:

    git push origin feature/your-feature-name

### Create a Pull Request:

Navigate to the original repository and click on "Compare & pull request" to submit your changes for review.

## Guidelines

-    Code Quality: Ensure your code follows Python best practices and is well-documented.
-    Testing: Test your changes thoroughly before submitting.
-    Documentation: Update the README.md or other documentation files if your changes affect usage or functionality.

### Example Workflow

Here's a step-by-step example of how to use Chisel to preprocess your image dataset:

#### Prepare Your Directories:

-    Input Folder: Place all raw images in ./raw_images.
-    Output Folder: Designate ./processed_images for storing processed images and metadata.

  #### Run Chisel: 

    python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --target_size 512 512 --output_format JPEG --min_size 150 --blur_threshold 120.0 --enhancement_factors 1.2 1.1 1.3 1.0 --quality 90

#### Review Logs:

#### Check preprocessing_log.txt for a detailed log of the preprocessing activities.

#### Inspect Processed Images:

#### Navigate to ./processed_images to find your enhanced and organized image dataset, ready for AI training.

## Troubleshooting

#### Image Not Processing:

-    Issue: Image is too small or too blurry.
-    Solution: Adjust --min_size and --blur_threshold parameters to be more lenient or ensure your dataset contains high-quality images.

  #### Dependency Errors:
  
-    Issue: Missing Python packages.
-    Solution: Ensure all dependencies are installed by running pip install -r requirements.txt. For issues with opencv-python, ensure you have the necessary system libraries.

#### Permission Errors:

-    Issue: Lack of permissions to read/write files.
-    Solution: Check directory permissions and ensure you have the necessary rights to access the folders.

## Acknowledgments

We extend our heartfelt gratitude to the following individuals, organizations, and tools that have made Chisel possible:

#### Image Sources

-    Unsplash: Providing high-quality, freely usable images.
-    Pixabay: A vast collection of free images and videos.
-    Flickr: A platform for sharing creative work and images.

 #### AI Frameworks

-    TensorFlow: An open-source platform for machine learning.
-    PyTorch: A deep learning framework that accelerates the path from research prototyping to production deployment.

#### Tools and Libraries

-    Pillow: Python Imaging Library for image processing.
-    NumPy: Fundamental package for scientific computing with Python.
-    OpenCV: Open Source Computer Vision Library.
-    tqdm: Fast, extensible progress bar for Python.
-    hashlib: Secure hashes and message digests.

#### Community and Contributors

-    Contributors: Special thanks to all the contributors who have participated in this project. Your efforts and dedication are greatly appreciated!
-    Community Support: Grateful for the continuous support and feedback from our community members.

 #### Inspiration and Support

-    Open Source Community: For being a constant source of inspiration and fostering a collaborative spirit.
-    Educators, Artists, Developers, and Researchers: Your innovative ideas and creative inputs drive our mission forward. Thank you for your invaluable contributions!

## Requirements

#### Ensure all dependencies are installed by running:

    pip install -r requirements.txt

#### requirements.txt

    Pillow
    numpy
    opencv-python
    tqdm

Ensure that you have the latest versions of these packages for optimal performance.

## License

Chisel is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. You are free to share and adapt the material as long as appropriate credit is given and any derivatives are distributed under the same license.

This project adheres to the highest standards of license compliance, ensuring that all utilized resources respect intellectual property rights and Creative Commons licenses.
Thank you for using Chisel! We hope it significantly enhances your AI training workflows by providing clean, high-quality, and ethically sourced image datasets.

---

## Bug Reporting 

Encounter a bug or issue? Please report it through: 

-  [GitHub Security Advisories](https://github.com/M1ck4/MichaelAngel.io/security/advisories)
-  [Email](mailto:michaelangelo_io@protonmail.com)
-  [Bug Report](https://github.com/M1ck4/MichaelAngel.io/blob/main/.github/ISSUE_TEMPLATE/2-feature_request.yml)

---

<div align="center">

## Contact

For questions, suggestions, or collaboration opportunities, feel free to reach out:

[![Facebook](https://img.shields.io/badge/Facebook-4267B2?logo=facebook&logoColor=white&style=for-the-badge)](https://www.facebook.com/profile.php?id=61566307182551)  [![Email](https://img.shields.io/badge/Email-Contact%20Us-blue?style=for-the-badge&logo=gmail&logoColor=white)](mailto:michaelangelo_io@protonmail.com) 

---

[![Clone](https://img.shields.io/badge/Clone-GitHub-blue?logo=github&style=flat-square)](https://github.com/M1ck4/MichaelAngel.io.git)
[![Fork](https://img.shields.io/badge/Fork-GitHub-blue?logo=github&style=flat-square)](https://github.com/M1ck4/MichaelAngel.io/fork)
</div>
