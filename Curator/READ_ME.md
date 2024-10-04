
# Curator

## Overview

**Curator** downloads images from multiple APIs, including Pixabay, Unsplash, Pexels, Flickr, and Google Custom Search Engine (CSE). It supports concurrent downloads and includes features such as rate limiting, duplicate checking, and email notifications for download reports.


## Features

- Download images from various sources (Pixabay, Unsplash, Pexels, Flickr, Google CSE).
- Supports concurrent downloads using a thread pool.
- Implements rate limiting to comply with API restrictions.
- Checks for duplicate images before downloading.
- Saves metadata for each downloaded image.
- Sends email notifications with download reports.
- Configurable via a YAML configuration file.
- Allows saving images directly to cloud storage services like AWS S3, Google Drive or Dropbox (INCOMPLETE)
- Allow users to select image resolutions before downloading.

## Requirements

- Python 3.x
- Required libraries: 

Core Libraries

    requests
    threadpoolctl
    Pillow
    opencv-python
    SQLAlchemy
    Flask
    FastAPI
    Celery
    beautifulsoup4
    pytest
    rich
    colorama
    matplotlib
    plotly
  
You can install the required libraries using either:

    pip install -r requirements.txt

```
pip install requests threadpoolctl Pillow opencv-python SQLAlchemy Flask FastAPI Celery beautifulsoup4 pytest rich colorama matplotlib plotly

```
## Configuration (config.yaml)

```
api_keys:
  pixabay:
    key: 'YOUR_PIXABAY_API_KEY'
  unsplash:
    key: 'YOUR_UNSPLASH_API_KEY'
  pexels:
    key: 'YOUR_PEXELS_API_KEY'
  flickr:
    key: 'YOUR_FLICKR_API_KEY'
  google_cse:
    key: 'YOUR_GOOGLE_CSE_API_KEY'
    search_engine_id: 'YOUR_SEARCH_ENGINE_ID'
rate_limits:
  pixabay:
    calls: 20
    period: 60
  unsplash:
    calls: 50
    period: 60
  pexels:
    calls: 45
    period: 60
email_settings:
  smtp_server: 'smtp.example.com'
  smtp_port: 587
  smtp_login: 'your_email@example.com'
  smtp_password: 'your_email_password'
  from_email: 'your_email@example.com'
  to_email: 'recipient_email@example.com'
search_terms:
  - nature
  - city
  - animals
  - space
  - ocean
max_images_per_term: 100
```

## Usage

Clone the repository:

    git clone https://github.com/M1ck4/generative-ai-image-downloader.git

Navigate to the project directory:

    cd MichaelAngel.io

Run the script:

    python Curator.py

## Logging

The script logs events and errors to a file named image_downloader.log. You can check this file for details on the downloading process, including successful and failed requests.
Metrics

The script tracks various metrics during the download process, including:

    Total images downloaded
    Total requests made
    Successful and failed requests
    Time spent on each API

## License

This project is licensed under the MIT License. Feel free to contribute or modify the code for your needs.


Contributing

Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request.


License

This project is licensed under the **Creative Commons Non-Commercial License**. You may copy and redistribute the material in any medium or format, adapt, remix, transform, and build upon the material for non-commercial purposes only. You must give appropriate credit, provide a link to the license, and indicate if changes were made.

For more details, please refer to the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).


For any inquiries or issues, please contact the developer
Acknowledgments

Thanks to the developers of the API services used in this project for providing access to their resources.

Pixabay: https://pixabay.com/

Unsplash: https://unsplash.com/

Pexels: https://www.pexels.com/

Flickr: https://www.flickr.com/
