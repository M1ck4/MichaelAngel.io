import cv2
import datetime
import yaml
import argparse
import logging
import smtplib
from email.mime.text import MIMEText
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import sys
import shutil
import json

def load_defaults():
    return {
        'input': {
            'path': '',
            'batch_mode': False,
            'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.mpeg', '.mpg', '.3gp']
        },
        'output': {
            'frames_directory': 'Frames',
            'image_formats': ['jpg'],  # Changed to a list
            'quality': 95
        },
        'extraction': {
            'interval': 60,
            'mode': 'interval'  # Only 'interval' mode is supported
        },
        'metadata': {
            'required_fields': ['movie_name', 'year', 'director', 'license', 'url'],
            'default_license': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0',
            'format': 'yaml',  # 'yaml' or 'json'
            'custom_fields': ['genre', 'language', 'duration']
        },
        'email': {
            'enabled': False,
            'smtp': {
                'server': '',
                'port': 587,
                'use_tls': True,
                'username': '',
                'password': ''
            },
            'notification': {
                'from_email': '',
                'to_email': '',
                'subject': 'FilmFrame: Frame Extraction Complete',
                'body_template': 'Frame extraction has completed for {movie_name}. Total frames extracted: {frame_count}'
            }
        },
        'processing': {
            'max_processes': 4,
            'show_progress': True,
            'skip_existing': True,
            'existing_dir_action': 'ask'  # Options: 'ask', 'overwrite', 'create_new', 'skip'
        },
        'logging': {
            'file': 'filmframe.log',
            'level': 'INFO',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'error_handling': {
            'save_error_report': True,
            'error_report_path': 'error_reports/'
        },
        'advanced': {
            'frame_filename_template': 'frame_{frame_number}',
            'preserve_timestamps': True,
            'use_gpu': False  # GPU acceleration flag
        }
    }

def load_config(config_file="config.yaml"):
    config = load_defaults()
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            yaml_config = yaml.safe_load(f)
            update_dict(config, yaml_config)
    else:
        logging.warning(f"Configuration file '{config_file}' not found. Using default settings.")
    return config

def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def parse_arguments(config):
    parser = argparse.ArgumentParser(
        description='''\
FilmFrame: A tool for extracting frames from movies.

Usage Examples:
    python filmframe.py -i movie.mp4 -t 60 --image-format jpg png
    python filmframe.py -i /path/to/movies/ -b --max-processes 8 --image-format jpg tiff bmp
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Input settings
    input_group = parser.add_argument_group('Input Settings')
    input_group.add_argument(
        '-i', '--input',
        help='Input movie file or directory path.\n'
             'Provide a single movie file or a directory containing multiple movies.',
        required=True
    )
    input_group.add_argument(
        '-b', '--batch-mode',
        help='Enable batch mode for processing multiple movies in a directory.',
        action='store_true'
    )

    # Output settings
    output_group = parser.add_argument_group('Output Settings')
    output_group.add_argument(
        '-o', '--output',
        help='Output directory for storing extracted frames.\n'
             'Default: Specified in config.yaml or "Frames".'
    )
    output_group.add_argument(
        '--image-format',
        help='Output image format(s). Specify one or more formats (e.g., jpg, png, bmp, tiff).\n'
             'Default: jpg.',
        nargs='+',  # Accept multiple formats
        metavar='FORMAT',
        dest='image_formats'
    )
    output_group.add_argument(
        '--quality',
        help='Image quality for JPEG format (1-100).\n'
             'Higher values mean better quality and larger file sizes.\n'
             'Default: 95.',
        type=int
    )

    # Extraction settings
    extraction_group = parser.add_argument_group('Frame Extraction Settings')
    extraction_group.add_argument(
        '-t', '--interval',
        help='Time interval between frames in seconds.\n'
             'Default: 60 seconds.',
        type=float
    )
    extraction_group.add_argument(
        '--mode',
        help='Extraction mode: "interval".\n'
             'Default: interval.',
        choices=['interval']
    )

    # Metadata settings
    metadata_group = parser.add_argument_group('Metadata Settings')
    metadata_group.add_argument(
        '--metadata-format',
        help='Metadata storage format: "yaml" or "json".\n'
             'Default: yaml.',
        choices=['yaml', 'json']
    )

    # Email settings
    email_group = parser.add_argument_group('Email Notification Settings')
    email_group.add_argument(
        '--email-enabled',
        help='Enable email notifications upon completion.',
        action='store_true'
    )
    email_group.add_argument(
        '--smtp-server',
        help='SMTP server address for sending emails.'
    )
    email_group.add_argument(
        '--smtp-port',
        help='SMTP server port. Default: 587.',
        type=int
    )
    email_group.add_argument(
        '--smtp-username',
        help='SMTP username for authentication.'
    )
    email_group.add_argument(
        '--from-email',
        help='Sender email address.'
    )
    email_group.add_argument(
        '--to-email',
        help='Recipient email address.'
    )
    email_group.add_argument(
        '--email-subject',
        help='Subject line for the email notification.'
    )
    email_group.add_argument(
        '--email-body',
        help='Body template for the email notification.\n'
             'Use placeholders like {movie_name} and {frame_count}.'
    )

    # Processing settings
    processing_group = parser.add_argument_group('Processing Settings')
    processing_group.add_argument(
        '--max-processes',
        help='Number of parallel threads for frame extraction.\n'
             'Set to 1 for sequential processing.\n'
             'Default: 4.',
        type=int
    )
    processing_group.add_argument(
        '--show-progress',
        help='Display a progress bar during processing.',
        action='store_true'
    )
    processing_group.add_argument(
        '--skip-existing',
        help='Skip extraction for existing frames to avoid reprocessing.',
        action='store_true'
    )
    processing_group.add_argument(
        '--existing-dir-action',
        help="Action when the output directory already exists:\n"
             "'ask' - Prompt the user (default).\n"
             "'overwrite' - Overwrite existing files.\n"
             "'create_new' - Create a new directory.\n"
             "'skip' - Skip processing this movie.",
        choices=['ask', 'overwrite', 'create_new', 'skip']
    )

    # Advanced settings
    advanced_group = parser.add_argument_group('Advanced Settings')
    advanced_group.add_argument(
        '--use-gpu',
        help='Enable GPU acceleration if available.',
        action='store_true'
    )

    # Logging settings
    logging_group = parser.add_argument_group('Logging Settings')
    logging_group.add_argument(
        '--log-level',
        help='Set the logging level.\n'
             'Options: DEBUG, INFO, WARNING, ERROR, CRITICAL.\n'
             'Default: INFO.',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    )

    args = parser.parse_args()

    # Update config with CLI arguments if provided
    if args.input:
        config['input']['path'] = args.input
    if args.batch_mode:
        config['input']['batch_mode'] = True
    if args.output:
        config['output']['frames_directory'] = args.output
    if args.image_formats:
        config['output']['image_formats'] = args.image_formats
    if args.quality is not None:
        config['output']['quality'] = args.quality
    if args.interval is not None:
        config['extraction']['interval'] = args.interval
    if args.mode:
        config['extraction']['mode'] = args.mode
    if args.metadata_format:
        config['metadata']['format'] = args.metadata_format
    if args.email_enabled:
        config['email']['enabled'] = True
    if args.smtp_server:
        config['email']['smtp']['server'] = args.smtp_server
    if args.smtp_port is not None:
        config['email']['smtp']['port'] = args.smtp_port
    if args.smtp_username:
        config['email']['smtp']['username'] = args.smtp_username
    if args.from_email:
        config['email']['notification']['from_email'] = args.from_email
    if args.to_email:
        config['email']['notification']['to_email'] = args.to_email
    if args.email_subject:
        config['email']['notification']['subject'] = args.email_subject
    if args.email_body:
        config['email']['notification']['body_template'] = args.email_body
    if args.max_processes is not None:
        config['processing']['max_processes'] = args.max_processes
    if args.show_progress:
        config['processing']['show_progress'] = True
    if args.skip_existing:
        config['processing']['skip_existing'] = True
    if args.existing_dir_action:
        config['processing']['existing_dir_action'] = args.existing_dir_action.lower()
    if args.use_gpu:
        config['advanced']['use_gpu'] = True
    if args.log_level:
        config['logging']['level'] = args.log_level.upper()

    return config

def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logging.info(f"Directory '{dir_path}' has been created.")
    else:
        logging.info(f"Directory '{dir_path}' already exists.")
    return dir_path

def get_unique_directory(base_path):
    counter = 1
    new_path = f"{base_path}_{counter}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base_path}_{counter}"
    return new_path

def extract_frames_sequential(movie_file, interval_in_seconds, output_dir, image_formats, quality, total_frames, fps, show_progress, use_gpu):
    try:
        if use_gpu:
            # Check if CUDA is available
            if not hasattr(cv2, 'cudacodec'):
                logging.warning("OpenCV is not compiled with CUDA support. Falling back to CPU processing.")
                use_gpu = False
                cap = cv2.VideoCapture(movie_file)
            else:
                cap = cv2.cudacodec.createVideoReader(movie_file)
        else:
            cap = cv2.VideoCapture(movie_file)

        if not cap.isOpened():
            logging.error(f"Failed to open video file {movie_file}.")
            return 0

        frame_interval = int(fps * interval_in_seconds)
        extracted_frames = 0
        frame_idx = 0

        if show_progress:
            progress_bar = tqdm(total=total_frames, desc="Processing frames", unit="frame")

        while True:
            if use_gpu:
                ret, gpu_frame = cap.nextFrame()
                if not ret:
                    break
                frame = gpu_frame.download()
            else:
                ret, frame = cap.read()
                if not ret:
                    break

            if frame_idx % frame_interval == 0:
                for image_format in image_formats:
                    frame_filename = os.path.join(output_dir, f"frame_{frame_idx:05d}.{image_format}")
                    if quality is not None and image_format.lower() in ['jpg', 'jpeg']:
                        result = cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                    else:
                        result = cv2.imwrite(frame_filename, frame)
                    if not result:
                        logging.error(f"Failed to save frame {frame_idx} in format '{image_format}'.")
                extracted_frames += 1  # Counts frames, not files

            frame_idx += 1
            if show_progress:
                progress_bar.update(1)

        cap.release()
        if show_progress:
            progress_bar.close()

        return extracted_frames
    except Exception as e:
        logging.error(f"Error during frame extraction: {e}")
        return 0

def extract_frames_multithreaded(movie_file, interval_in_seconds, output_dir, image_formats, quality, total_frames, fps, max_threads, show_progress, use_gpu):
    try:
        frame_interval = int(fps * interval_in_seconds)
        extracted_frames = 0

        def process_frames(start_frame, end_frame):
            local_extracted_frames = 0
            try:
                if use_gpu:
                    if not hasattr(cv2, 'cudacodec'):
                        logging.warning("OpenCV is not compiled with CUDA support. Falling back to CPU processing.")
                        cap = cv2.VideoCapture(movie_file)
                    else:
                        cap = cv2.cudacodec.createVideoReader(movie_file)
                else:
                    cap = cv2.VideoCapture(movie_file)

                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                frame_idx = start_frame

                while frame_idx < end_frame:
                    if use_gpu:
                        ret, gpu_frame = cap.nextFrame()
                        if not ret:
                            break
                        frame = gpu_frame.download()
                    else:
                        ret, frame = cap.read()
                        if not ret:
                            break

                    if frame_idx % frame_interval == 0:
                        for image_format in image_formats:
                            frame_filename = os.path.join(output_dir, f"frame_{frame_idx:05d}.{image_format}")
                            if quality is not None and image_format.lower() in ['jpg', 'jpeg']:
                                result = cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                            else:
                                result = cv2.imwrite(frame_filename, frame)
                            if not result:
                                logging.error(f"Failed to save frame {frame_idx} in format '{image_format}'.")
                        local_extracted_frames += 1  # Counts frames, not files

                    frame_idx += 1

                cap.release()
            except Exception as e:
                logging.error(f"Error in thread processing frames {start_frame} to {end_frame}: {e}")
            return local_extracted_frames

        frames_per_thread = total_frames // max_threads
        ranges = []
        for i in range(max_threads):
            start_frame = i * frames_per_thread
            end_frame = start_frame + frames_per_thread
            if i == max_threads - 1:
                end_frame = total_frames  # Ensure the last thread processes until the end
            ranges.append((start_frame, end_frame))

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(process_frames, start, end) for start, end in ranges]

            if show_progress:
                for future in tqdm(futures, desc="Processing threads"):
                    extracted_frames += future.result()
            else:
                for future in futures:
                    extracted_frames += future.result()

        return extracted_frames
    except Exception as e:
        logging.error(f"Error during multithreaded frame extraction: {e}")
        return 0

def store_metadata(metadata, output_file, format='yaml'):
    try:
        with open(output_file, 'w') as f:
            if format == 'yaml':
                yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
            elif format == 'json':
                json.dump(metadata, f, indent=4)
        logging.info(f"Metadata stored in '{output_file}'.")
    except Exception as e:
        logging.error(f"Error storing metadata: {e}")

def send_email_notification(email_config, movie_name, frame_count):
    try:
        body = email_config['notification']['body_template'].format(
            movie_name=movie_name,
            frame_count=frame_count
        )
        msg = MIMEText(body)
        msg['Subject'] = email_config['notification']['subject']
        msg['From'] = email_config['notification']['from_email']
        msg['To'] = email_config['notification']['to_email']

        server = smtplib.SMTP(email_config['smtp']['server'], email_config['smtp']['port'])
        if email_config['smtp'].get('use_tls', True):
            server.starttls()
        server.login(email_config['smtp']['username'], email_config['smtp']['password'])
        server.send_message(msg)
        server.quit()
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email notification: {e}")

def process_movie(movie_info, config, master_metadata):
    movie_file = movie_info['movie_file']
    movie_name = movie_info['movie_name']
    logging.info(f"Processing movie '{movie_name}'.")

    # Create output directory for frames
    frames_dir = os.path.join(config['output']['frames_directory'], movie_name)
    if os.path.exists(frames_dir):
        action = config['processing'].get('existing_dir_action', 'ask')
        if action == 'ask':
            if not config['input']['batch_mode']:
                # In non-batch mode, ask the user
                while True:
                    user_input = input(f"Directory '{frames_dir}' already exists. Do you want to overwrite the images in this directory? (y/n): ").strip().lower()
                    if user_input == 'y':
                        # Overwrite images
                        logging.info(f"Overwriting images in '{frames_dir}'.")
                        # Remove existing files in the directory
                        for filename in os.listdir(frames_dir):
                            file_path = os.path.join(frames_dir, filename)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        action = 'overwrite'  # Update action
                        break
                    elif user_input == 'n':
                        # Create a new directory
                        frames_dir = get_unique_directory(frames_dir)
                        logging.info(f"Creating new directory '{frames_dir}' for new images.")
                        create_directory(frames_dir)
                        action = 'create_new'  # Update action
                        break
                    else:
                        print("Please enter 'y' or 'n'.")
            else:
                # In batch mode, default to 'create_new'
                frames_dir = get_unique_directory(frames_dir)
                logging.info(f"Creating new directory '{frames_dir}' for new images.")
                create_directory(frames_dir)
        elif action == 'overwrite':
            logging.info(f"Overwriting images in '{frames_dir}'.")
            # Remove existing files in the directory
            for filename in os.listdir(frames_dir):
                file_path = os.path.join(frames_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        elif action == 'create_new':
            frames_dir = get_unique_directory(frames_dir)
            logging.info(f"Creating new directory '{frames_dir}' for new images.")
            create_directory(frames_dir)
        elif action == 'skip':
            logging.info(f"Skipping existing directory '{frames_dir}'.")
            return  # Skip processing this movie
        else:
            logging.error(f"Unknown existing_dir_action '{action}'.")
            return
    else:
        create_directory(frames_dir)

    # Video properties
    cap = cv2.VideoCapture(movie_file)
    if not cap.isOpened():
        logging.error(f"Failed to open video file {movie_file}.")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames / fps
    cap.release()

    # Collect metadata
    metadata = {
        "movie_name": movie_name,
        "year": movie_info.get("year"),
        "director": movie_info.get("director"),
        "license": movie_info.get("license", config['metadata']['default_license']),
        "url": movie_info.get("url"),
        "genre": movie_info.get("genre"),
        "language": movie_info.get("language"),
        "duration": total_duration,
        "frames": []
    }

    # Extract frames using optimized methods
    max_processes = config['processing'].get('max_processes', 4)
    use_gpu = config['advanced'].get('use_gpu', False)

    if max_processes > 1:
        extracted_frames = extract_frames_multithreaded(
            movie_file=movie_file,
            interval_in_seconds=config['extraction']['interval'],
            output_dir=frames_dir,
            image_formats=config['output']['image_formats'],
            quality=config['output'].get('quality', None),
            total_frames=total_frames,
            fps=fps,
            max_threads=max_processes,
            show_progress=config['processing']['show_progress'],
            use_gpu=use_gpu
        )
    else:
        extracted_frames = extract_frames_sequential(
            movie_file=movie_file,
            interval_in_seconds=config['extraction']['interval'],
            output_dir=frames_dir,
            image_formats=config['output']['image_formats'],
            quality=config['output'].get('quality', None),
            total_frames=total_frames,
            fps=fps,
            show_progress=config['processing']['show_progress'],
            use_gpu=use_gpu
        )

    if extracted_frames == 0:
        logging.error(f"No frames extracted for movie '{movie_name}'.")
        return

    # Update metadata
    frame_numbers = set()
    for image_format in config['output']['image_formats']:
        frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.' + image_format)]
        for f in frame_files:
            frame_number = int(f.split('_')[1].split('.')[0])
            frame_numbers.add(frame_number)

    frame_numbers = sorted(frame_numbers)
    for frame_number in frame_numbers:
        files = [f"frame_{frame_number:05d}.{fmt}" for fmt in config['output']['image_formats']]
        metadata['frames'].append({'frame_number': frame_number, 'files': files})

    # Store per-movie metadata
    metadata_file = os.path.join(frames_dir, f"metadata.{config['metadata']['format']}")
    store_metadata(metadata, metadata_file, format=config['metadata']['format'])

    # Append to master metadata
    master_metadata.append(metadata)

    # Send email notification if enabled
    if config['email']['enabled']:
        send_email_notification(config['email'], movie_name, extracted_frames)

    logging.info(f"Completed processing for movie '{movie_name}'.")

def main():
    # Load configuration from YAML file or defaults
    config = load_config("config.yaml")

    # Parse command-line arguments and override config
    config = parse_arguments(config)

    # Setup logging
    logging.basicConfig(
        filename=config['logging']['file'],
        level=getattr(logging, config['logging']['level'].upper(), logging.INFO),
        format=config['logging']['format']
    )
    # Add console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config['logging']['level'].upper(), logging.INFO))
    console_handler.setFormatter(logging.Formatter(config['logging']['format']))
    logging.getLogger('').addHandler(console_handler)

    # Create output directories
    create_directory(config['output']['frames_directory'])
    if config['error_handling']['save_error_report']:
        create_directory(config['error_handling']['error_report_path'])

    # Prepare movie files
    input_path = config['input']['path']
    batch_mode = config['input']['batch_mode']
    supported_formats = config['input']['supported_formats']

    if not input_path:
        logging.error("No input path specified. Please provide an input path via CLI or config.yaml.")
        sys.exit(1)

    master_metadata = []

    if batch_mode:
        if not os.path.isdir(input_path):
            logging.error(f"Input path '{input_path}' is not a directory.")
            sys.exit(1)

        movie_files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                       if os.path.splitext(f)[1].lower() in supported_formats]
        if not movie_files:
            logging.error("No movie files found in the directory.")
            sys.exit(1)

        # Collect movie information
        movies_info = []
        for movie_file in movie_files:
            movie_name = os.path.splitext(os.path.basename(movie_file))[0]
            movie_info = {
                'movie_file': movie_file,
                'movie_name': movie_name
            }
            # Collect additional metadata if required
            for field in config['metadata']['required_fields']:
                if field not in movie_info or not movie_info[field]:
                    value = input(f"Enter '{field}' for '{movie_name}': ")
                    movie_info[field] = value
            # Collect custom fields
            for field in config['metadata'].get('custom_fields', []):
                if field not in movie_info or not movie_info[field]:
                    value = input(f"Enter '{field}' for '{movie_name}': ")
                    movie_info[field] = value
            movies_info.append(movie_info)

        # Process movies sequentially
        for movie_info in movies_info:
            process_movie(movie_info, config, master_metadata)
    else:
        if not os.path.exists(input_path):
            logging.error(f"Input path '{input_path}' does not exist.")
            sys.exit(1)

        if os.path.isdir(input_path):
            logging.error(f"Input path '{input_path}' is a directory. Use batch mode for directories.")
            sys.exit(1)

        movie_name = os.path.splitext(os.path.basename(input_path))[0]
        movie_info = {
            'movie_file': input_path,
            'movie_name': movie_name
        }
        # Collect additional metadata if required
        for field in config['metadata']['required_fields']:
            if field not in movie_info or not movie_info[field]:
                value = input(f"Enter '{field}' for '{movie_name}': ")
                movie_info[field] = value
        # Collect custom fields
        for field in config['metadata'].get('custom_fields', []):
            if field not in movie_info or not movie_info[field]:
                value = input(f"Enter '{field}' for '{movie_name}': ")
                movie_info[field] = value

        process_movie(movie_info, config, master_metadata)

    # Store master metadata
    if master_metadata:
        master_metadata_file = os.path.join(config['output']['frames_directory'], f"master_metadata.{config['metadata']['format']}")
        if config['metadata']['format'] == 'yaml':
            with open(master_metadata_file, 'w') as f:
                yaml.dump(master_metadata, f, default_flow_style=False, sort_keys=False)
        elif config['metadata']['format'] == 'json':
            with open(master_metadata_file, 'w') as f:
                json.dump(master_metadata, f, indent=4)
        logging.info(f"Master metadata stored in '{master_metadata_file}'.")

if __name__ == "__main__":
    main()
