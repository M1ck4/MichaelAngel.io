import cv2
import datetime
import yaml
import argparse
import logging
import smtplib
from email.mime.text import MIMEText
import os


def detect_movie_format(movie_file):
    try:
        cap = cv2.VideoCapture(movie_file)
        return cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    except Exception as e:
        logging.error(f"Error detecting movie format: {e}")
        return None


def extract_frames(movie_file, interval):
    try:
        cap = cv2.VideoCapture(movie_file)
        frames = []
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % interval == 0:
                frames.append(frame)
            frame_count += 1
        cap.release()
        return frames
    except Exception as e:
        logging.error(f"Error extracting frames: {e}")
        return None


def collect_metadata(frame):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = {'timestamp': timestamp}
        return metadata
    except Exception as e:
        logging.error(f"Error collecting metadata: {e}")
        return None


def store_metadata(metadata, output_file):
    try:
        metadata_dict = {
            "movie_name": metadata["movie_name"],
            "year": metadata["year"],
            "director": metadata["director"],
            "license": metadata["license"],
            "url": metadata["url"],
            "frames": metadata["frames"]
        }
        with open(output_file, 'w') as f:
            yaml.dump(metadata_dict, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        logging.error(f"Error storing metadata: {e}")


def send_email_notification(email_address, subject, body, smtp_server, from_email):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = email_address
        server = smtplib.SMTP(smtp_server)
        server.sendmail(from_email, email_address, msg.as_string())
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
    """ Ensure a unique directory name by appending '_1', '_2', etc. if it already exists. """
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
    parser.add_argument('-t', '--interval', help='Frame extraction interval in seconds', type=int, required=True)
    parser.add_argument('-b', '--batch', help='Batch mode', action='store_true')
    args = parser.parse_args()

    input_path = args.input
    interval = args.interval
    batch_mode = args.batch

    frames_dir = 'Frames'
    create_directory(frames_dir)

    if batch_mode:
        if os.path.isdir(input_path):
            movie_files = [f for f in os.listdir(input_path) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            configs = []
            for movie_file in movie_files:
                print(f"\nMovie file: {movie_file}")
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

                send_email = input("\nWould you like to send an email notification? (y/n): ")
                if send_email.lower() == 'y':
                    email_address = input("Email address: ")
                    smtp_server = input("SMTP server: ")
                    from_email = input("From email address: ")
                    subject = "FrameFilm: Operation Complete"
                    body = "The frame extraction operation has completed successfully."
                    configs.append({
                        "movie_name": movie_name,
                        "year": year,
                        "director": director,
                        "license": license,
                        "url": url,
                        "send_email": True,
                        "email_address": email_address,
                        "smtp_server": smtp_server,
                        "from_email": from_email,
                        "subject": subject,
                        "body": body,
                        "movie_file": movie_file
                    })
                else:
                    configs.append({
                        "movie_name": movie_name,
                        "year": year,
                        "director": director,
                        "license": license,
                        "url": url,
                        "send_email": False,
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
                frames = extract_frames(movie_file, interval)
                if frames is None:
                    print("Error: Failed to extract frames.")
                    continue
                metadata = {
                    "movie_name": config["movie_name"],
                    "year": config["year"],
                    "director": config["director"],
                    "license": config["license"],
                    "url": config["url"],
                    "frames": []
                }
                for i, frame in enumerate(frames):
                    timestamp = collect_metadata(frame)
                    metadata["frames"].append({
                        "timestamp": timestamp["timestamp"],
                        "frame_number": i
                    })
                output_file = os.path.join(movie_dir, "metadata.yaml")
                store_metadata(metadata, output_file)
                for i, frame in enumerate(frames):
                    cv2.imwrite(os.path.join(movie_dir, f"frame_{i}.jpg"), frame)
                if config["send_email"]:
                    send_email_notification(config["email_address"], config["subject"], config["body"],
                                            config["smtp_server"], config["from_email"])
                print("Operation complete for movie", config["movie_name"])
        else:
            print("Error: Input path is not a directory.")
    else:
        if os.path.isfile(input_path):
            movie_file = input_path
            print(f"\nMovie file: {movie_file}")
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

            send_email = input("\nWould you like to send an email notification? (y/n): ")
            if send_email.lower() == 'y':
                email_address = input("Email address: ")
                smtp_server = input("SMTP server: ")
                from_email = input("From email address: ")
                subject = "FrameFilm: Operation Complete"
                body = "The frame extraction operation has completed successfully."
                config = {
                    "movie_name": movie_name,
                    "year": year,
                    "director": director,
                    "license": license,
                    "url": url,
                    "send_email": True,
                    "email_address": email_address,
                    "smtp_server": smtp_server,
                    "from_email": from_email,
                    "subject": subject,
                    "body": body,
                    "movie_file": movie_file
                }
            else:
                config = {
                    "movie_name": movie_name,
                    "year": year,
                    "director": director,
                    "license": license,
                    "url": url,
                    "send_email": False,
                    "movie_file": movie_file
                }
            movie_dir = os.path.join(frames_dir, config["movie_name"])

            if os.path.exists(movie_dir):
                overwrite = input(f"Directory '{movie_dir}' already exists. Overwrite? (y/n): ")
                if overwrite.lower() != 'y':
                    movie_dir = get_unique_directory(movie_dir)

            create_directory(movie_dir)
            frames = extract_frames(movie_file, interval)
            if frames is None:
                print("Error: Failed to extract frames.")
                return
            metadata = {
                "movie_name": config["movie_name"],
                "year": config["year"],
                "director": config["director"],
                "license": config["license"],
                "url": config["url"],
                "frames": []
            }
            for i, frame in enumerate(frames):
                timestamp = collect_metadata(frame)
                metadata["frames"].append({
                    "timestamp": timestamp["timestamp"],
                    "frame_number": i
                })
            output_file = os.path.join(movie_dir, "metadata.yaml")
            store_metadata(metadata, output_file)
            for i, frame in enumerate(frames):
                cv2.imwrite(os.path.join(movie_dir, f"frame_{i}.jpg"), frame)
            if config["send_email"]:
                send_email_notification(config["email_address"], config["subject"], config["body"],
                                        config["smtp_server"], config["from_email"])
            print("Operation complete.")
        else:
            print("Error: Input path is not a file.")


if __name__ == "__main__":
    main()
