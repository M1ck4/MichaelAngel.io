import cv2
import datetime
import yaml
import argparse
import logging
import smtplib
from email.mime.text import MIMEText
import os
import getpass  # For secure password input
from tqdm import tqdm  # For progress bar


def detect_movie_format(movie_file):
    try:
        cap = cv2.VideoCapture(movie_file)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cap.release()
        return width, height
    except Exception as e:
        logging.error(f"Error detecting movie format: {e}")
        return None


def extract_frames(movie_file, interval_in_seconds):
    try:
        cap = cv2.VideoCapture(movie_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            logging.error("FPS is zero, cannot proceed.")
            return None
        frame_interval = int(fps * interval_in_seconds)
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                yield frame, frame_count
            frame_count += 1
        cap.release()
    except Exception as e:
        logging.error(f"Error extracting frames: {e}")
        return None


def collect_metadata():
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = {'timestamp': timestamp}
        return metadata
    except Exception as e:
        logging.error(f"Error collecting metadata: {e}")
        return None


def store_metadata(metadata, output_file):
    try:
        with open(output_file, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        logging.error(f"Error storing metadata: {e}")


def send_email_notification(email_config):
    try:
        msg = MIMEText(email_config['body'])
        msg['Subject'] = email_config['subject']
        msg['From'] = email_config['from_email']
        msg['To'] = email_config['to_email']

        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['username'], email_config['password'])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logging.error(f"Error sending email notification: {e}")


def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory '{dir_path}' has been created.")
    else:
        print(f"Directory '{dir_path}' already exists.")
    return dir_path


def get_unique_directory(base_path):
    if not os.path.exists(base_path):
        return base_path
    counter = 1
    new_path = f"{base_path}_{counter}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base_path}_{counter}"
    return new_path


def main():
    parser = argparse.ArgumentParser(description='FrameFilm: A tool for extracting frames from movies')
    parser.add_argument('-i', '--input', help='Input movie file or directory', required=True)
    parser.add_argument('-o', '--output', help='Output directory for frames (optional)')
    parser.add_argument('-t', '--interval', help='Frame extraction interval in seconds', type=float, required=True)
    parser.add_argument('-b', '--batch', help='Batch mode', action='store_true')
    parser.add_argument('--email', help='Enable email notification', action='store_true')
    parser.add_argument('--smtp-server', help='SMTP server address')
    parser.add_argument('--smtp-port', help='SMTP server port', type=int, default=587)
    parser.add_argument('--smtp-username', help='SMTP username')
    parser.add_argument('--from-email', help='From email address')
    parser.add_argument('--to-email', help='To email address')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--image-format', help='Output image format (e.g., jpg, png)', default='jpg')

    args = parser.parse_args()

    input_path = args.input
    interval_in_seconds = args.interval
    batch_mode = args.batch
    email_enabled = args.email
    image_format = args.image_format.lower()

    # Validate image format
    valid_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    if image_format not in valid_formats:
        print(f"Invalid image format '{image_format}'. Supported formats are: {', '.join(valid_formats)}.")
        return

    frames_dir = args.output if args.output else 'Frames'
    create_directory(frames_dir)

    # Email configuration
    email_config = {}
    if email_enabled:
        if not all([args.smtp_server, args.smtp_username, args.from_email, args.to_email]):
            print("Error: Email notification is enabled, but not all email arguments are provided.")
            return
        smtp_password = getpass.getpass(prompt='SMTP Password: ')
        email_config = {
            'smtp_server': args.smtp_server,
            'smtp_port': args.smtp_port,
            'username': args.smtp_username,
            'password': smtp_password,
            'from_email': args.from_email,
            'to_email': args.to_email,
            'subject': args.subject if args.subject else 'FrameFilm: Operation Complete',
            'body': args.body if args.body else 'The frame extraction operation has completed successfully.'
        }

    if batch_mode:
        if os.path.isdir(input_path):
            movie_files = [f for f in os.listdir(input_path) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            if not movie_files:
                print("No movie files found in the directory.")
                return
            configs = []
            for movie_file in movie_files:
                print(f"\nProcessing movie file: {movie_file}")
                movie_name = input("Movie Name: ")
                while True:
                    try:
                        year = int(input("Year: "))
                        break
                    except ValueError:
                        print("Invalid year. Please enter a valid integer.")
                director = input("Director: ")
                license = input("License: ")
                url = input("URL: ")

                print("\nPlease confirm the following information:")
                print(f"Movie Name: {movie_name}")
                print(f"Year: {year}")
                print(f"Director: {director}")
                print(f"License: {license}")
                print(f"URL: {url}")

                confirm = input("\nIs this information correct? (y/n): ")
                if confirm.lower() != 'y':
                    print("Please re-enter the information.")
                    return main()

                configs.append({
                    "movie_name": movie_name,
                    "year": year,
                    "director": director,
                    "license": license,
                    "url": url,
                    "movie_file": movie_file
                })

            for config in configs:
                movie_file = os.path.join(input_path, config["movie_file"])
                movie_dir = os.path.join(frames_dir, config["movie_name"])

                if os.path.exists(movie_dir):
                    overwrite = input(f"Directory '{movie_dir}' already exists. Overwrite? (y/n): ")
                    if overwrite.lower() != 'y':
                        movie_dir = get_unique_directory(movie_dir)

                create_directory(movie_dir)
                metadata = {
                    "movie_name": config["movie_name"],
                    "year": config["year"],
                    "director": config["director"],
                    "license": config["license"],
                    "url": config["url"],
                    "frames": []
                }

                print("Extracting frames...")
                frame_gen = extract_frames(movie_file, interval_in_seconds)
                if frame_gen is None:
                    print("Error: Failed to extract frames.")
                    continue

                total_frames = int(cv2.VideoCapture(movie_file).get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cv2.VideoCapture(movie_file).get(cv2.CAP_PROP_FPS)
                frame_interval = int(fps * interval_in_seconds)
                estimated_frames = total_frames // frame_interval

                for frame, frame_count in tqdm(frame_gen, total=estimated_frames, desc="Processing Frames"):
                    frame_filename = os.path.join(movie_dir, f"frame_{frame_count}.{image_format}")
                    cv2.imwrite(frame_filename, frame)
                    timestamp = collect_metadata()
                    metadata["frames"].append({
                        "timestamp": timestamp["timestamp"],
                        "frame_number": frame_count,
                        "file": frame_filename
                    })

                output_file = os.path.join(movie_dir, "metadata.yaml")
                store_metadata(metadata, output_file)

                if email_enabled:
                    send_email_notification(email_config)

                print(f"Operation complete for movie '{config['movie_name']}'")
        else:
            print("Error: Input path is not a directory.")
    else:
        if os.path.isfile(input_path):
            movie_file = input_path
            print(f"\nProcessing movie file: {movie_file}")
            movie_name = input("Movie Name: ")
            while True:
                try:
                    year = int(input("Year: "))
                    break
                except ValueError:
                    print("Invalid year. Please enter a valid integer.")
            director = input("Director: ")
            license = input("License: ")
            url = input("URL: ")

            print("\nPlease confirm the following information:")
            print(f"Movie Name: {movie_name}")
            print(f"Year: {year}")
            print(f"Director: {director}")
            print(f"License: {license}")
            print(f"URL: {url}")

            confirm = input("\nIs this information correct? (y/n): ")
            if confirm.lower() != 'y':
                print("Please re-enter the information.")
                return main()

            movie_dir = os.path.join(frames_dir, movie_name)

            if os.path.exists(movie_dir):
                overwrite = input(f"Directory '{movie_dir}' already exists. Overwrite? (y/n): ")
                if overwrite.lower() != 'y':
                    movie_dir = get_unique_directory(movie_dir)

            create_directory(movie_dir)
            metadata = {
                "movie_name": movie_name,
                "year": year,
                "director": director,
                "license": license,
                "url": url,
                "frames": []
            }

            print("Extracting frames...")
            frame_gen = extract_frames(movie_file, interval_in_seconds)
            if frame_gen is None:
                print("Error: Failed to extract frames.")
                return

            total_frames = int(cv2.VideoCapture(movie_file).get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cv2.VideoCapture(movie_file).get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * interval_in_seconds)
            estimated_frames = total_frames // frame_interval

            for frame, frame_count in tqdm(frame_gen, total=estimated_frames, desc="Processing Frames"):
                frame_filename = os.path.join(movie_dir, f"frame_{frame_count}.{image_format}")
                cv2.imwrite(frame_filename, frame)
                timestamp = collect_metadata()
                metadata["frames"].append({
                    "timestamp": timestamp["timestamp"],
                    "frame_number": frame_count,
                    "file": frame_filename
                })

            output_file = os.path.join(movie_dir, "metadata.yaml")
            store_metadata(metadata, output_file)

            if email_enabled:
                send_email_notification(email_config)

            print("Operation complete.")
        else:
            print("Error: Input path is not a file.")


if __name__ == "__main__":
    main()
