
# Curator (IN DEVELOPMENT)

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

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
