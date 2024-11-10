# FilmFrame

FilmFrame is a Python-based tool for extracting frames from movies and collecting metadata associated with them. Designed with artists, researchers, and developers in mind, FilmFrame allows you to capture frames at regular intervals from video files, save them in multiple image formats, and store metadata in structured files. The tool also supports GPU acceleration for faster processing and can send email notifications upon completion of frame extraction.

## Features

- **Extract Frames:** Extract frames from video files at specified time intervals.
- **Multiple Image Formats:** Save extracted frames in one or more image formats (e.g., JPG, PNG, BMP, TIFF).
- **Batch Mode:** Process multiple movie files in a directory.
- **Metadata Collection:** Capture metadata such as timestamps, frame numbers, and additional details about the movie (e.g., movie name, year, director, license).
- **Master Metadata File:** Generate a master metadata file aggregating information from all processed movies.
- **GPU Acceleration:** Optionally use GPU acceleration for faster frame extraction (requires OpenCV built with CUDA support).
- **Email Notification:** Optionally send an email notification upon completion of the frame extraction process.
- **Frame Storage:** Save extracted frames in designated directories with customizable naming conventions.

## Requirements

- **Python 3.7+**
- **Dependencies:**
  - OpenCV (`opencv-python>=4.5.1`)
  - PyYAML (`pyyaml>=5.4`)
  - tqdm (`tqdm>=4.0.0`)
- **Optional for GPU Acceleration:**
  - OpenCV built with CUDA support (not available via `pip`; must be compiled manually)
- **SMTP Email Server (optional, for email notifications)**

## Installation

1. **Clone this repository:**
   ```sh
   git clone https://github.com/M1ck4/MichaelAngel.io
   ```

2. **Navigate to the project directory:**
   ```sh
   cd filmframe
   ```

3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **GPU Acceleration (Optional):**

   To use GPU acceleration, you need to compile OpenCV with CUDA support. Follow OpenCV's official documentation for instructions on building OpenCV with CUDA.

5. **Set up an SMTP email server (Optional):**

   If you wish to use the email notification feature, ensure you have access to an SMTP server. Configure the SMTP settings in the `config.yaml` file or provide them via command-line arguments.

## Configuration

The tool uses a `config.yaml` file for default settings. You can modify this file to set default values for various options such as input paths, output directories, image formats, and more.

```yaml
# Example config.yaml snippet
input:
  path: "path/to/movies"
  batch_mode: false

output:
  frames_directory: "Frames"
  image_formats:
    - "jpg"
    - "png"
    - "bmp"
    - "tiff"
  quality: 95

extraction:
  interval: 60
  mode: "interval"

# ... rest of the configuration ...
```

## Usage

The script can be run in either single mode (for individual movie files) or batch mode (for multiple movie files in a directory). You must specify the input movie file or directory, as well as the frame extraction interval in seconds.

### Single Mode (Extract frames from one movie file)

```sh
python filmframe.py -i <movie_file> -t <interval_in_seconds>
```

**Example:**

```sh
python filmframe.py -i my_movie.mp4 -t 60 --image-format jpg png
```

This command extracts frames from `my_movie.mp4` every 60 seconds and saves them in both JPG and PNG formats.

### Batch Mode (Extract frames from multiple movie files in a directory)

```sh
python filmframe.py -i <directory> -t <interval_in_seconds> -b
```

**Example:**

```sh
python filmframe.py -i /path/to/movies/ -t 60 -b --image-format jpg png bmp tiff
```

This command processes all supported video files in `/path/to/movies/`, extracts frames every 60 seconds, and saves them in JPG, PNG, BMP, and TIFF formats.

### Enabling GPU Acceleration (Optional)

To use GPU acceleration (if you have OpenCV compiled with CUDA support):

```sh
python filmframe.py -i my_movie.mp4 -t 60 --use-gpu
```

### Email Notification (Optional)

To enable email notifications upon completion:

1. **Configure SMTP Settings:**
   - Edit the `config.yaml` file to include your SMTP server details and email addresses.
   - Alternatively, provide the settings via command-line arguments.

2. **Run the Script with Email Enabled:**

   ```sh
   python filmframe.py -i my_movie.mp4 -t 60 --email-enabled
   ```

### Additional Options

- `-o` or `--output`: Specify the output directory for storing extracted frames.
- `--max-processes`: Set the number of parallel threads for frame extraction (default is 4).
- `--metadata-format`: Choose the metadata file format (`yaml` or `json`).

### Example Workflow

1. **Run the script in batch mode to process a folder of movies:**
   ```sh
   python filmframe.py -i /path/to/movies/ -t 60 -b --image-format jpg png
   ```

2. **Provide Metadata:**
   The script will prompt you to input metadata for each movie (e.g., movie name, year, director, license, URL). This metadata is necessary for compliance with Creative Commons licensing and for organizing your frames.

3. **Review Outputs:**
   Extracted frames and associated metadata are saved in directories named after each movie within the specified output directory. A master metadata file (`master_metadata.yaml` or `master_metadata.json`) is generated in the root output directory, aggregating metadata from all processed movies.

4. **Optional Email Notification:**
   If email notifications are enabled, you will receive an email upon completion of the frame extraction process.

**Example with Multiple Features:**

```sh
python filmframe.py -i my_movie.mp4 -t 120 --use-gpu --email-enabled --output /path/to/output --image-format jpg png --metadata-format json
```

This command extracts frames every 120 seconds from `my_movie.mp4`, uses GPU acceleration, enables email notifications, and saves frames in both JPG and PNG formats with metadata stored in JSON format in the specified output directory.

## Supported Image Formats

FilmFrame supports saving frames in multiple image formats. Supported formats include:

- **JPEG** (`jpg`, `jpeg`)
- **PNG** (`png`)
- **BMP** (`bmp`)
- **TIFF** (`tiff`, `tif`)

Specify the desired formats using the `--image-format` command-line argument or by editing the `config.yaml` file.

**Example:**

```sh
python filmframe.py -i my_movie.mp4 -t 60 --image-format jpg png bmp tiff
```

## Metadata

- **Per-Movie Metadata:**
  - Stored in a `metadata.yaml` or `metadata.json` file within each movie's frames directory.
  - Includes movie details and a list of extracted frames with associated file names.

- **Master Metadata File:**
  - Aggregated metadata from all processed movies.
  - Saved as `master_metadata.yaml` or `master_metadata.json` in the root output directory.

- **Metadata Fields:**
  - Required fields: `movie_name`, `year`, `director`, `license`, `url`.
  - Custom fields: `genre`, `language`, `duration`, etc.

**Example Metadata Entry:**

```yaml
movie_name: "Inception"
year: 2010
director: "Christopher Nolan"
license: "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"
url: "https://example.com/inception"
frames:
  - file_name: "frame_001.jpg"
    timestamp: "00:01:00"
  - file_name: "frame_002.jpg"
    timestamp: "00:02:00"
```

## Notes on GPU Acceleration

- **Requirements:**
  - OpenCV must be compiled with CUDA support.
  - A compatible NVIDIA GPU with the appropriate CUDA drivers.

- **Usage:**
  - Enable GPU acceleration by adding the `--use-gpu` flag when running the script.
  - The script will automatically fall back to CPU processing if GPU acceleration is not available.

- **Performance:**
  - GPU acceleration can significantly speed up frame extraction, especially for high-resolution videos.

## Error Handling and Logging

- **Logging:**
  - Logs are saved to a file specified in the `config.yaml` file (default is `filmframe.log`).
  - Logging level can be adjusted (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

- **Error Reports:**
  - If enabled, error reports are saved in the specified error report directory.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license.

FilmFrame is designed for educational and non-commercial use. Please ensure proper attribution when using any extracted frames or metadata.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on the GitHub repository.

## Disclaimer

Please respect all applicable laws and licenses when using this tool. Ensure that you have the right to process and extract frames from the video files you use.

## Bug Reporting 

Encounter a bug or issue? Please report it through: 

-  [GitHub Security Advisories](https://github.com/M1ck4/MichaelAngel.io/security/advisories)
-  [Email](mailto:michaelangelo_io@protonmail.com)
-  [Bug Report](https://github.com/M1ck4/MichaelAngel.io/blob/main/.github/ISSUE_TEMPLATE/2-feature_request.yml)

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
