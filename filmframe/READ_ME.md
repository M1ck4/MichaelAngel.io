# FilmFrame

FrameFilm is a Python-based tool for extracting frames from movies and collecting metadata associated with them. This tool is especially useful for artists, researchers, and developers who need to capture frames at regular intervals from video files and store the metadata in a structured format. The tool also supports email notifications once the frame extraction is complete.

## Features

- **Extract Frames**: Extracts frames from video files at specified time intervals.
- **Batch Mode**: Processes multiple movie files in a directory.
- **Metadata Collection**: Captures metadata such as timestamps for each frame and allows users to input additional details about the movie (e.g., movie name, year, director, license, etc.).
- **Email Notification**: Optionally sends an email notification upon completion of the frame extraction process.
- **Frame Storage**: Saves extracted frames as JPEG images in designated directories.

## Requirements

- Python 3.7+
- OpenCV (`cv2`)
- PyYAML
- SMTP Email Server (optional, for email notifications)

## Installation

1. Clone this repository:

       git clone https://github.com/M1cKa/FilmFrame.git
Navigate to the project directory:

    cd FilmFrame

Install the required dependencies:

    pip install -r requirements.txt

Set up an SMTP email server (optional) if you wish to use the email notification feature.

Usage

The script can be run in either single mode (for individual movie files) or batch mode (for multiple movie files in a directory). You must specify the input movie file or directory, as well as the frame extraction interval in seconds.
Single Mode (Extract frames from one movie file)

    python FilmFrame.py -i <movie_file> -t <interval_in_seconds>

Example:

    python filmframe.py -i my_movie.mp4 -t 60

Batch Mode (Extract frames from multiple movie files in a directory)

    python filmframe.py -i <directory> -t <interval_in_seconds> -b

    python filmframe.py -i /path/to/movies/ -t 60 -b

Email Notification (Optional)

The script can send an email notification upon completion of the extraction process.

During the execution of the script, it will ask if you'd like to send an email notification.
Provide the necessary email information (recipient, SMTP server, etc.).

Metadata

During the extraction process, you will be asked to provide metadata for each movie (e.g., movie name, year, director, license, and URL). This metadata, along with frame information (timestamps, frame numbers), will be stored in a metadata.yaml file within the output directory.
Options

-i or --input: The input movie file or directory containing movie files (required).
-o or --output: Output directory for storing extracted frames (optional).
-t or --interval: The time interval (in seconds) between frames to be extracted (required).
-b or --batch: Enable batch mode to process multiple movie files in a directory (optional).

Example Workflow

Run the script in batch mode to process a folder of movies.
Input metadata such as movie name, year, director, and license when prompted.
The extracted frames and associated metadata will be saved in a directory named after each movie.
Optionally receive an email notification when the extraction is complete.

License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license.

FilmFrame is designed for educational and non-commercial use. Please ensure proper attribution when using any extracted frames or metadata.
