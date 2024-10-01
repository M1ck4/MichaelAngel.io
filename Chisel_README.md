# Chisel

## Overview

Chisel is a powerful, user-friendly image processing tool designed to enhance, organize, and optimize your image collections. Built with flexibility and accessibility in mind, it serves a wide range of users from artists to scientists, making it an essential addition to any digital toolkit.

## Key Features

Image Enhancement: Apply a variety of filters to enhance image quality, including brightness, contrast, saturation, and sharpness adjustments.

Batch Processing: Process multiple images at once, saving time and effort in large projects.

Format Conversion: Easily convert images between popular formats (JPEG, PNG, GIF, etc.) to meet project requirements.

Image Resizing: Resize images while maintaining aspect ratio, making it easy to prepare images for specific use cases.

Watermarking: Add custom watermarks to images for branding or copyright protection.

Metadata Management: Edit and manage image metadata for better organization and searchability.

Custom Filters: Create and apply your own filters using Python, allowing for unique image transformations.

User-Friendly Interface: Designed for ease of use, with a simple command-line interface that guides users through each function.

Integration with Other Tools: Seamlessly integrate with other Python libraries for expanded functionality (e.g., NumPy, OpenCV).

Attribution Compliance: Automatically generate attribution text files for Creative Commons images, ensuring compliance with usage rights.

Error Handling: Comprehensive error handling and logging, providing users with clear feedback on any issues encountered during processing.

Documentation and Support: Detailed documentation and a support community available to assist users in troubleshooting and maximizing the tool’s potential.

## Who Will Use Chisel

Photographers: Enhance and organize their photo collections, applying filters and adjustments for portfolio presentation.

Graphic Designers: Utilize image processing capabilities for creative projects, such as advertising materials or digital art.

Digital Artists: Enhance and manipulate images for artwork, applying custom filters and effects to achieve unique styles.

Social Media Managers: Optimize images for social media platforms, ensuring high-quality visuals that meet specific size and format requirements.

Content Creators and Influencers: Enhance images for blogs, videos, and social media posts, making them more visually appealing to attract and engage audiences.

Filmmakers and Video Editors: Process still images for use in film projects, optimizing visuals for storyboarding or promotional materials.

Web Developers: Optimize images on websites, improving load times while maintaining visual quality for better user experience.

Marketing Professionals: Enhance images for branding and promotional campaigns, ensuring compliance with copyright and attribution requirements.

Educators and Students: Use in educational settings for projects involving image analysis or enhancement, promoting hands-on learning experiences.

Healthcare Professionals: Analyze and enhance medical imaging data, supporting diagnostics and research.

Archivists and Curators: Manage and preserve digital collections, ensuring the quality and organization of historical or artistic images.

Non-Profit Organizations: Process images for campaigns or educational materials, ensuring they are of high quality and compliant with usage rights.

Scientists and Researchers: Process and analyze images from experiments, ensuring quality and compliance with publication standards.

Machine Learning Engineers: Preprocess images for training datasets, ensuring high quality and consistency in image attributes.

Hobbyists and DIY Enthusiasts: Use for personal projects involving photography, crafting, or digital art, enhancing their creative endeavors.

## Installation

To install Chisel.py, follow these steps:

Clone the repository:

    git clone https://github.com/M1ck4/MichaelAngel.io.git

Navigate to the project directory:

    cd MichaelAngel.io

Install the required dependencies using the requirements file:

    pip install -r chisel_requirements.txt

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

Here are some example CLI Commands

Enhance an image:

    python chisel.py enhance --input image.jpg --output enhanced_image.jpg --brightness 1.2 --contrast 1.5

Batch process images:

    python chisel.py batch --input_folder images/ --output_folder processed_images/ --resize 800x600

Add watermark:

    python chisel.py watermark --input image.jpg --output watermarked_image.jpg --watermark watermark.png

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


