### Modules FAQ

**What is the `modules` folder?**

The `modules` folder is the core directory of the MichaelAngel.io Framework, containing each major component designed to support ethical AI and media processing workflows. Each subfolder in `modules` represents a unique tool, developed to handle different stages of data acquisition, processing, and dataset management.

**What tools are housed in the `modules` folder, and what does each one do?**

1. **Chisel**  
   Chisel is the preprocessing tool that prepares raw images for dataset inclusion. It ensures that all media assets meet quality and format standards needed for AI model training.  
   *Features:*
   - **Resizing and Quality Control**: Automatically resizes images to specified dimensions, ensuring consistency across datasets.
   - **Image Enhancement**: Detects and corrects issues like blurriness or low contrast, maintaining high-quality data standards.
   - **Metadata Retention**: Carries forward all attribution and metadata, supporting legal compliance at every stage.

2. **Curator**  
   Curator is the downloader module, focused on sourcing images and other media from Creative Commons websites. It’s built for large-scale downloads and gathers detailed metadata with each item.  
   *Features:*
   - **API Integrations**: Seamlessly connects to popular Creative Commons sites (e.g., Unsplash, Pixabay, Pexels, Flickr) and other sources for media.
   - **Multi-threaded Downloading**: Supports fast, concurrent downloads through a multi-threaded setup to handle large datasets efficiently.
   - **Detailed Metadata Collection**: Captures comprehensive metadata such as author, license, URL, and any Creative Commons requirements, ensuring each file is well-documented.
   - **Duplicate Detection**: Cross-references downloaded files with a master attribute file to prevent duplicate downloads.

3. **FilmFrame**  
   FilmFrame is a tool designed to extract frames from Creative Commons films, bridging the gap between film and AI-driven creativity.  
   *Features:*
   - **Frame Extraction**: Allows users to queue multiple films and extract specific frames at set intervals or based on user-defined parameters.
   - **Batch Processing**: Processes multiple movies at once, saving all frames in designated folders for efficient access.
   - **File Format Options**: Offers various file format outputs (JPEG, PNG) and saves extracted frames directly to cloud storage, enhancing accessibility.
   - **Automatic Metadata Tagging**: Extracts and stores metadata for each frame, facilitating easy organization and attribution.

4. **Muse**  
   Muse is the dataset manager that organizes all preprocessed media into structured datasets, ready for AI training. It’s also responsible for handling labels, data augmentation, and preparing datasets in an optimized format for the MichaelAngel.io model.  
   *Features:*
   - **Dataset Creation**: Organizes images, labels, and metadata into structured, user-friendly datasets tailored to AI model requirements.
   - **Dataset Splitting**: Automatically splits datasets into training, validation, and test sets for seamless AI model training preparation.
   - **Data Augmentation**: Offers options for transformations like flipping, rotation, and scaling to enhance dataset diversity.
   - **Automatic Labeling and Metadata Generation**: Generates tags and labels based on image content, leveraging tools like TagTuner.
   - **Format Conversion**: Exports datasets in formats optimized for deep learning frameworks, making it straightforward to load into MichaelAngelo or other AI models.

**Why is each module independently developed?**

This modular setup ensures flexibility, scalability, and ease of maintenance. Users can run individual tools on specific tasks or combine them in sequence for a complete AI data pipeline. This approach also enables specialized improvements to each module without impacting the others, supporting the framework's commitment to ethical and high-quality data processing.

**How do these modules interact within the MichaelAngel.io Framework?**

Each tool is designed to perform distinct tasks within the AI development pipeline:
   - **Curator** acquires media, ensuring legal compliance and high-quality downloads.
   - **Chisel** preprocesses the acquired images, standardizing them for use in machine learning.
   - **FilmFrame** expands the dataset with diverse visual resources from film media.
   - **Muse** brings everything together, creating well-structured and labeled datasets for immediate use.

In essence, these modules provide a seamless workflow from data acquisition to model-ready datasets, enabling ethical AI development while maintaining high data standards. For more details on each tool, please refer to their specific README files within each subfolder.

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>

