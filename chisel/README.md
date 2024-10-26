# Chisel

## Overview

Chisel is a robust and user friendly image processing tool crafted to enhance, organize, and optimize your image collections effortlessly. Designed for a diverse range of users from artists and photographers to educators and researchers—Chisel is an essential companion in any digital toolkit. With its seamless integration, powerful features, and intuitive interface, Chisel empowers you to elevate your visual content with precision and ease

## Key Features

**Image Enhancement:** Transform your images with advanced filters that boost quality. Adjust brightness, contrast, saturation, and sharpness to create stunning visuals that captivate your audience.

**Batch Processing:** Save valuable time by processing multiple images simultaneously. Whether you’re working on a large project or simply need to enhance a collection, Chisel makes it efficient.

**Format Conversion:**  Easily convert images between popular formats (JPEG, PNG, GIF, etc.) to fit your project needs. Chisel ensures compatibility across various applications.

**Image Resizing:**  Maintain aspect ratios while resizing images to prepare them for specific use cases. Perfect for optimizing images for social media, print, or web use.

**Metadata Management:**  Edit and manage image metadata for improved organization and searchability, ensuring that you keep track of copyright and attribution details.

**Custom Filters:**  Harness the power of Python to create and apply your own filters, allowing for unique image transformations tailored to your artistic vision.

**Error Handling and Logging:**  Comprehensive error handling provides clear feedback on processing issues, while logging keeps you informed about each step taken.

**Attribution Compliance:**  Automatically generate attribution text files for Creative Commons images, ensuring you remain compliant with usage rights effortlessly.

**Documentation and Support:**  Access detailed documentation and a supportive community ready to assist you in maximizing Chisel’s potential.

## Who Will Use Chisel

**Texture Artists:** Easily resize textures, apply color correction, and create consistent texture variants.

**Photographers:** Enhance and organize collections for stunning portfolio presentations.

**Graphic Designers:** Utilize Chisel's processing capabilities for creative projects, such as marketing materials and digital art.

**Digital Artists:** Apply custom filters and effects to enhance artwork, achieving unique styles that stand out.

**Social Media Managers:** Optimize images to ensure high-quality visuals that meet platform-specific requirements.

**Filmmakers and Video Editors:** Process still images for storyboarding or promotional materials.

**Web Developers:** Improve website performance by optimizing images for faster load times while maintaining visual quality.

**Marketing Professionals:** Enhance visuals for branding campaigns, ensuring compliance with copyright and attribution requirements.

**Researchers and Scientists:** Process and analyze images from experiments, ensuring quality and adherence to publication standards.

## Installation

To install Chisel.py, follow these steps:

Clone the repository:

    git clone https://github.com/M1ck4/MichaelAngel.io.git

Navigate to the project directory:

    cd MichaelAngel.io

Install the required dependencies using the requirements file:

    pip install -r requirements.txt

## Usage

The very basic use of chisel is:

    python chisel.py --input_folder /path/to/input_folder --output_folder /path/to/output_folder

Chisel has pretermined defaults and when only the input folder and output folder is given defualts are applied.

## Predefined Defaults in Chisel

Chisel comes with sensible defaults to ensure a smooth user experience right out of the box. Below are the predefined default settings for various parameters in the application:

Input Folder:            

    Default: ./input
This is the folder where Chisel looks for images to process if no input folder is specified.

Output Folder:

    Default: ./processed
This is the destination folder for processed images. If the folder does not exist, Chisel will create it automatically.

Image Format:

    Default: JPEG
This is the default format in which processed images will be saved. Supported formats include JPEG, PNG, and TIFF.

Resize:
    
    Default: false
Images will not be resized unless specified. To enable resizing, you must provide width and height in the command.


Resize Dimensions (when enabled):

    Default Width: 800
    Default Height: 600
These dimensions apply if resizing is enabled.


Quality:

    Default: 85
This setting determines the quality of the processed images on a scale of 0 to 100. A higher number results in better quality at the cost of larger file size.


Overwrite:

    Default: false
Chisel will not overwrite existing files in the output folder by default. You must specify the --overwrite flag to allow overwriting.
To use Chisel with the many options it has, run the following command in your terminal:

    python chisel.py --help

This command will display a list of available options and how to use them. Each feature is designed with user-friendliness in mind, guiding you through the process of enhancing and organizing your images.

## Command Line Interface (CLI) Help

Chisel comes equipped with a user-friendly command line interface that provides easy access to its powerful features. You can view the available commands and options by running:

    python chisel.py --help

When you run the --help command, you'll see the following key options and features that Chisel offers:
Basic Commands

    --input or -i: 
Specify the input directory containing the images you want to preprocess. This option allows you to easily point Chisel to the source images you wish to enhance.

    --output or -o: 
Define the output directory where the processed images will be saved. This helps you maintain an organized workflow and ensures that your original images remain untouched.

Preprocessing Options

    --resize
Resize images to specified dimensions. This feature is perfect for optimizing images for different platforms or print sizes without losing quality.

    --crop 
Crop images to focus on the essential elements. This can help improve composition and remove unnecessary background noise from images.

    --enhance
Apply various enhancement filters to improve image quality. This option includes sharpening, brightness adjustment, and contrast enhancement, ensuring your images look their best.

    --format or -f
Convert images to different formats (e.g., JPG, PNG, BMP). This feature ensures compatibility with various applications and platforms.

Batch Processing

    --batch
Process multiple images in a single command. This feature saves time and increases efficiency when working with large datasets or collections of images.

Metadata Management

    --metadata
Include metadata preservation options to keep track of the original image data. This is crucial for photographers and artists who need to maintain copyright and attribution information.

Preview and Logging

    --preview
Generate a preview of the processed images before saving. This allows you to make quick adjustments and ensures satisfaction with the final output.

    --log
Enable logging to track the processing steps and any issues that arise. This feature is particularly useful for debugging and maintaining a clear workflow.

## Example Commands

Enhance an image:

    python chisel.py enhance --input image.jpg --output enhanced_image.jpg --brightness 1.2 --contrast 1.5

Batch process images:

    python chisel.py batch --input_folder images/ --output_folder processed_images/ --resize 2048x2048

Batch Processing with watermark and resizing to 1024x1024 and saving in .jpeg at 100% quality:

    python chisel.py --input /path/to/input_folder --output /path/to/output_folder --resize --width 1024 --height 1024 --format JPEG --quality 100

Convert all PNG images in a folder to JPEG:

    python chisel.py --input /path/to/input_folder --output /path/to/output_folder --format JPEG --batch

Resize Without Overwriting Existing Files Resize images while ensuring existing files are not overwritten:

    python chisel.py --input /path/to/input_folder --output /path/to/output_folder --resize --width 800 --height 600 --quality 85 --overwrite false



## Configuration Files

Chisel supports the use of configuration files to customize your preprocessing workflow. This feature allows you to define various parameters and settings in a centralized manner, making it easier to manage and reuse configurations across different projects.
Creating a Configuration File

File Format: The configuration file should be in JSON format for easy readability and compatibility.

Example Configuration: Below is an example of what a configuration file (config.json) might look like:

    json

    {
        "input_folder": "C:/images/input",
        "output_folder": "C:/images/processed",
        "resize": {
            "enabled": true,
            "width": 800,
            "height": 600
        },
        "format": "JPEG",
        "quality": 85
    }

Parameters Explained:

    input_folder: The directory containing the images to be processed.    
    output_folder: The directory where processed images will be saved.
    resize: A boolean indicating whether to resize images, with width and height specifying the new dimensions.
    format: The desired format for the processed images (e.g., JPEG, PNG).
    quality: The quality level for formats that support it, on a scale of 0 to 100.

Using a Configuration File

To run Chisel with a configuration file, use the following command:

    python chisel.py --config /path/to/config.json


Benefits of Using Configuration Files

Simplifies Workflow: By defining settings in a config file, you can streamline your processing commands, reducing command-line clutter.

Easier Management: Changes to parameters can be made directly in the config file without needing to modify command-line arguments each time.

Reusable Settings: Save and share configuration files for different projects or team members, ensuring consistency in processing.


NOTE: Configuration Files are curretnly being made, they should be uploaded soon. 

<div align="center">

## Contact

For questions, suggestions, or collaboration opportunities, feel free to reach out:

[![Facebook](https://img.shields.io/badge/Facebook-4267B2?logo=facebook&logoColor=white&style=for-the-badge)](https://www.facebook.com/profile.php?id=61566307182551)  [![Email](https://img.shields.io/badge/Email-Contact%20Us-blue?style=for-the-badge&logo=gmail&logoColor=white)](mailto:michaelangelo_io@protonmail.com)  

[![GitHub Profile](https://img.shields.io/badge/GitHub-Profile-181717?logo=github&logoColor=white&style=for-the-badge)](https://github.com/M1ck4)

</div>


