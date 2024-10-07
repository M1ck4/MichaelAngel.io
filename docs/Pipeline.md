# AI Pipeline Overview

## 1. Curator (Downloader)

- **When to Use:** At the beginning of the pipeline or when requiring new Creative Commons images.  
- **Purpose:** Downloads Creative Commons images from various APIs.  
- **Process:**  
  - Define search terms or categories for image collection.  
  - Pull images and metadata, ensuring they meet basic requirements (e.g., file format, resolution).  
  - Store images in an organized structure by source or category.  
  - Extract and manage metadata (tags, licenses) for easier access and utilization.

---

## 2.A. FilmFrame (Frame Extractor)

- **When to Use:** After Curator completes its task or when only requiring frames from movie files.  
- **Purpose:** Extracts frames from movies and generates associated metadata for dataset creation.  
- **Process:**  
  - Identify movie files or directories containing movies.  
  - Extract frames at specified intervals to capture key moments.  
  - Collect metadata for each movie (e.g., movie name, year, director, license, URL).  
  - Store metadata in a structured format (e.g., YAML) for easy access and management.  
- **Output:** A directory of extracted frames and a metadata file for each movie processed.

---

## 2. Chisel (Preprocessor)

- **When to Use:** After FilmFrame extracts frames or after Curator finishes downloading.  
- **Purpose:** Prepares images for dataset creation by ensuring quality and size.  
- **Process:**  
  - Resize images while preserving aspect ratio.  
  - Remove blurry images.  
  - Clean up noisy or artifact-ridden files.  
  - Check against the master attributes file to avoid duplicates.  
- **Output:** A cleaned and standardized set of images stored in a separate directory.

---

## 3. Muse (Dataset Creator and Manager)

- **When to Use:** After Chisel preprocesses the images.  
- **Purpose:** Organizes preprocessed images into structured datasets for training.  
- **Process:**  
  - Split images into training, validation, and test sets.  
  - Label images based on metadata or categories.  
  - Apply data augmentation (e.g., rotations, flips) if desired.  
  - Convert images and annotations into the required format (e.g., TFRecord, COCO).  
  - Export the final dataset for easy access.  
- **Output:** A fully organized dataset ready for MichaelAngelo.

---

## 4. MichaelAngelo (Main AI Model)

- **When to Use:** Once Muse has created the dataset.  
- **Purpose:** The main ethical generative model for training new images.  
- **Process:**  
  - Load the dataset from Muse.  
  - Define the model architecture (e.g., GAN, VAE).  
  - Train the model using various techniques (e.g., transfer learning).  
  - Evaluate performance and adjust hyperparameters as needed.  
- **Output:** A trained generative model capable of creating new images.

---

## Alternate Workflow

- **Musing After Curator:**  
  If exploring new categories or sources, running Muse right after Curator for quick management of datasets. However, run Chisel first to ensure high-quality data before any dataset management.
