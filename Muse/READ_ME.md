# Muse (INCOMPLETE)



Muse is a powerful dataset creation and management tool designed to organize, label, and optimize preprocessed images for AI model training. It integrates seamlessly with the Chisel preprocessing tool and is an essential part of the image-to-AI pipeline, leading to the creation of high-quality, structured datasets ready for training on models like **MichaelAngelo**.

## Features

- **Dataset Splitting**: Automatically divide your image collection into training, validation, and test sets, with customizable split ratios.
- **Labeling**: Apply labels to images based on metadata or defined categories, ensuring that your dataset is well-structured for training.
- **Data Augmentation**: Enhance your dataset by applying augmentation techniques like rotations, flips, and crops, boosting dataset diversity and improving AI performance.
- **Format Conversion**: Convert images and annotations into the required formats for popular AI frameworks, including TensorFlow's TFRecord and the COCO format for object detection tasks.
- **Export and Optimization**: Save the dataset in an organized and optimized structure, ensuring fast loading times and efficient access during AI model training.

## Workflow

Muse is designed to be used after **Chisel** has finished preprocessing the images. The typical workflow includes:

1. **Preprocessing**: Feed images preprocessed by Chisel into Muse.
2. **Dataset Splitting**: Divide the images into training, validation, and test sets based on your desired ratios.
3. **Labeling**: Automatically or manually label images based on metadata or custom categories.
4. **Augmentation (Optional)**: Apply data augmentation techniques to increase dataset variety.
5. **Format Conversion**: Convert images and annotations into the required format for your AI framework (e.g., TFRecord, COCO).
6. **Exporting**: Export the fully labeled, organized, and augmented dataset in a structure optimized for training.

## License

This project is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

As long as you follow the license terms, including giving appropriate credit, providing a link to the license, and indicating if changes were made.


