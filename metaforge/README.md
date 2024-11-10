# Metaforge

Metaforge is the centralized database and metadata management tool within the MichaelAngel.io Framework. It serves as the backbone for metadata storage, handling, and retrieval, ensuring all project assets maintain accurate and accessible attribution throughout the AI development pipeline.

## Overview

Metaforge plays a crucial role in managing metadata for every asset within the MichaelAngel.io Framework, maintaining legal and ethical compliance with Creative Commons and other licenses. The tool includes a suite of components to handle complex metadata operations, supporting efficient data access and traceability.

## Core Files

- **metadata_manager.py**: The primary interface for managing metadata entries, allowing for data insertion, updates, and queries.
- **models.py**: Contains the database models that structure how metadata is stored and accessed.
- **schemas.py**: Defines the data schemas for ensuring consistency and validation of metadata entries.
- **utils.py**: Provides utility functions to support metadata operations and database management.
- **requirements.txt**: Lists the dependencies necessary for running Metaforge.

## Features

- **Comprehensive Metadata Storage**: Supports structured storage of metadata fields such as author, license type, source URL, file format, and more.
- **Database Operations**: Efficient querying, updating, and retrieval of metadata records to facilitate data usage across the MichaelAngel.io Framework.
- **Compliance Management**: Ensures Creative Commons and other licenses are correctly tracked and recorded throughout each stage of the AI pipeline.

## Installation

To set up Metaforge, clone the repository and install the dependencies specified in `requirements.txt`:

```bash
git clone https://github.com/M1ck4/Metaforge.git
cd Metaforge
pip install -r requirements.txt
```

## Usage

Run Metaforge by initializing the database and utilizing `metadata_manager.py` for managing metadata:

```bash
python metadata_manager.py --action <insert|update|query> --data <metadata_input_file>
```

## Example Commands

- **Insert new metadata entries**:

```bash
python metadata_manager.py --action insert --data ./metadata.json
```

- **Update existing metadata**:

```bash
python metadata_manager.py --action update --data ./update_metadata.json
```

- **Query metadata for reporting or integration**:

```bash
python metadata_manager.py --action query --filter author:<author_name>
```

## Configuration

Metaforge is configured using a `config.yaml` file where you can define database settings, logging preferences, and API credentials.

## License

Metaforge is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. For more details, see the LICENSE file.

<div align="center">

---

## Contact

For questions, suggestions, or collaboration opportunities, feel free to reach out:

[![Email](https://img.shields.io/badge/Email-Contact%20Us-blue?style=for-the-badge&logo=gmail&logoColor=white)](mailto:michaelangelo_io@protonmail.com) 

[![Clone](https://img.shields.io/badge/Clone-GitHub-blue?logo=github&style=flat-square)](https://github.com/M1ck4/MichaelAngel.io.git)

---
![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)

</div>
