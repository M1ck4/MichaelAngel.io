# Chisel

Chisel is a powerful preprocessing tool designed to enhance image datasets by filtering out low-quality images and preparing them for AI training. It ensures that your dataset is both high-quality and ethically sound, streamlining the workflow for artists, developers, and researchers.

## Overview

Chisel serves as the preprocessing powerhouse within the MichaelAngel.io pipeline. Its primary function is to filter out low-quality images and prepare them for AI training by performing the following tasks:

- Quality Control: Removes duplicates and low-quality images based on size and blurriness.
- Consistent Resizing: Ensures all images meet specified dimensions for uniformity.
- Metadata Preservation: Retains essential metadata and attribution information.
- Batch Processing: Efficiently handles large volumes of images using parallel processing.

By automating these critical preprocessing steps, Chisel ensures that your image datasets are clean, organized, and ready for AI-driven creative projects.

## Features

- **Automated Quality Checks**: Filters images based on size and blurriness to maintain high dataset quality.
- **Metadata Extraction**: Extracts and preserves EXIF metadata for comprehensive dataset information.
- **Duplicate Detection**: Identifies and removes duplicate images using content hashing.
- **Image Enhancement**: Enhances image properties such as brightness, contrast, color, and sharpness.
- **Flexible Output Formats**: Supports saving processed images in JPEG, PNG, or NumPy array formats.
- **Efficient Processing**: Utilizes parallel processing to handle large datasets swiftly.
- **Comprehensive Logging**: Logs all preprocessing activities for transparency and troubleshooting.

## Installation

### Prerequisites

- Python 3.8+
- Git

### Clone the Repository

```sh
git clone https://github.com/M1ck4/MichaelAngel.io.git
```

### Navigate to the Chisel Directory

```sh
cd MichaelAngel.io/chisel
```

### Create a Virtual Environment (Optional but Recommended)

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

Ensure you have pip installed, then run:

```sh
pip install -r requirements.txt
```

If you encounter issues with specific packages, ensure you have the necessary system libraries installed, especially for `opencv-python`.

## Usage

Chisel can be executed via the command line with various arguments to customize its behavior.

### Command-Line Arguments

```sh
python Chisel.py --image_folder <input_folder> --output_folder <output_folder> [options]
```

#### Required Arguments

- `image_folder`: Path to the input folder containing images to be processed.
- `output_folder`: Path to the output folder where processed images and metadata will be saved.

#### Optional Arguments

- `target_size`: Target size for image resizing in the format `width height`. Default is `256 256`.
- `output_format`: Output format for processed images. Choices are `JPEG`, `PNG`, `numpy`. Default is `JPEG`.
- `min_size`: Minimum size (in pixels) for image quality. Images smaller than this will be excluded. Default is `128`.
- `blur_threshold`: Blur threshold for image quality check. Images with blurriness below this threshold will be excluded. Default is `100.0`.
- `enhancement_factors`: Enhancement factors for brightness, contrast, color, and sharpness in the format `brightness contrast color sharpness`. Default is `1.0 1.0 1.0 1.0`.
- `quality`: Quality for JPEG output (1-100). Default is `85`.

### Example Usages

#### Process images using default settings

```sh
python Chisel.py --image_folder ./raw_images --output_folder ./processed_images
```

This command processes images from `./raw_images`, resizes them to `256x256`, and saves them in JPEG format.

#### Specifying Output Format

Save processed images in PNG format instead of the default JPEG.

```sh
python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --output_format PNG
```

#### Adjusting Image Size

Resize images to custom dimensions.

```sh
python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --target_size 512 512
```

#### Enhancing Image Properties

Enhance brightness and contrast of images.

```sh
python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --enhancement_factors 1.2 1.1 1.0 1.0
```

#### Combining Multiple Options

Perform advanced preprocessing with custom settings.

```sh
python Chisel.py --image_folder ./raw_images --output_folder ./processed_images --target_size 512 512 --output_format numpy --min_size 150 --blur_threshold 120.0 --enhancement_factors 1.2 1.1 1.3 1.0 --quality 90
```

## Configuration

Chisel provides flexibility through various command-line arguments, allowing you to tailor the preprocessing pipeline to your specific needs.

### Image Quality Parameters

- **Minimum Size (`--min_size`)**: Ensures that only images above a certain resolution are included.
- **Blur Threshold (`--blur_threshold`)**: Filters out blurry images based on variance in Laplacian.

### Image Enhancement Factors (`--enhancement_factors`)

- **Brightness**: Adjusts the brightness level.
- **Contrast**: Modifies the contrast of the image.
- **Color**: Alters the color saturation.
- **Sharpness**: Changes the sharpness of the image.

### Output Settings

- **Target Size (`--target_size`)**: Specifies the dimensions to which images will be resized.
- **Output Format (`--output_format`)**: Determines the format in which processed images are saved.
- **Quality (`--quality`)**: Sets the quality level for JPEG images.

## Logging

Chisel maintains a comprehensive log of all preprocessing activities to facilitate transparency and troubleshooting. The logs are saved in a file named `preprocessing_log.txt` located in the root directory of the Chisel project.

### Example Log Entries

```
2024-04-27 12:34:56,789 - INFO - Starting preprocessing for images in ./raw_images
2024-04-27 12:35:01,123 - INFO - Image ./raw_images/image1.jpg is too small.
2024-04-27 12:35:05,456 - ERROR - Error processing ./raw_images/image2.jpg: [Errno 2] No such file or directory
2024-04-27 12:35:10,789 - INFO - Successfully processed and saved ./raw_images/image3.jpg
```

## Contributing

We welcome contributions to enhance Chisel and make it even more robust and user-friendly. Whether you're fixing bugs, adding new features, or improving documentation, your efforts are highly appreciated!

### How to Contribute

1. **Fork the Repository**: Click the "Fork" button at the top-right corner of the repository page to create a personal copy.

2. **Clone Your Fork**:

   ```sh
   git clone https://github.com/M1ck4/MichaelAngel.io.git
   ```

3. **Create a New Branch**:

   ```sh
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**: Implement your feature or bug fix.

5. **Commit Your Changes**:

   ```sh
   git commit -m "Add feature: your feature description"
   ```

6. **Push to Your Fork**:

   ```sh
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**: Navigate to the original repository and click on "Compare & pull request" to submit your changes for review.

### Guidelines

- **Code Quality**: Ensure your code follows Python best practices and is well-documented.
- **Testing**: Test your changes thoroughly before submitting.
- **Documentation**: Update the `README.md` or other documentation files if your changes affect usage or functionality.

## Troubleshooting

### Image Not Processing

- **Issue**: Image is too small or too blurry.
- **Solution**: Adjust `--min_size` and `--blur_threshold` parameters to be more lenient or ensure your dataset contains high-quality images.

### Dependency Errors

- **Issue**: Missing Python packages.
- **Solution**: Ensure all dependencies are installed by running `pip install -r requirements.txt`. For issues with `opencv-python`, ensure you have the necessary system libraries.

### Permission Errors

- **Issue**: Lack of permissions to read/write files.
- **Solution**: Check directory permissions and ensure you have the necessary rights to access the folders.

## Acknowledgments

We extend our heartfelt gratitude to the following individuals, organizations, and tools that have made Chisel possible:

### Image Sources

- **Unsplash**: Providing high-quality, freely usable images.
- **Pixabay**: A vast collection of free images and videos.
- **Flickr**: A platform for sharing creative work and images.

### AI Frameworks

- **TensorFlow**: An open-source platform for machine learning.
- **PyTorch**: A deep learning framework that accelerates the path from research prototyping to production deployment.

### Tools and Libraries

- **Pillow**: Python Imaging Library for image processing.
- **NumPy**: Fundamental package for scientific computing with Python.
- **OpenCV**: Open Source Computer Vision Library.
- **tqdm**: Fast, extensible progress bar for Python.
- **hashlib**: Secure hashes and message digests.

### Community and Contributors

- **Contributors**: Special thanks to all the contributors who have participated in this project.
- **Community Support**: Grateful for the continuous support and feedback from our community members.

### Inspiration and Support

- **Open Source Community**: For being a constant source of inspiration and fostering a collaborative spirit.
- **Educators, Artists, Developers, and Researchers**: Your innovative ideas and creative inputs drive our mission forward.

## Requirements

Ensure all dependencies are installed by running:

```sh
pip install -r requirements.txt
```

### `requirements.txt`

- `Pillow`
- `numpy`
- `opencv-python`
- `tqdm`

Ensure that you have the latest versions of these packages for optimal performance.
