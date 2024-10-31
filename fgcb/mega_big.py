from LLM import LLM
from interpret_execute_choice import scroll_maybe, send_request, endpoints

import os
import time
import requests
from pathlib import Path

import logging

# Directory where recordings are saved
output_directory = "./screen_recordings/"


def get_latest_files(directory, n=1):
    # Get all files in the directory
    files = [f for f in os.listdir(directory) if f.startswith("clip_") and f.endswith(".mp4")]

    # Sort files based on their creation time
    files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)

    # Return the latest 'n' files
    return files[:n]

def check_helpers():
    logging.info("Pinging helper services...")
    try:
        response = requests.get("http://localhost:4000/status")
        response = requests.get("http://localhost:8000/status")
    except requests.exceptions.RequestException as e:
        logging.error("Error pinging helper service: %s", e)
        exit(1)


def get_clip():
    latest_file = output_directory / Path(get_latest_files(output_directory, n=2)[1])
    logging.info("Latest file retrieved: %s", latest_file.resolve().as_posix())

    if not latest_file:
        logging.warning("No video files found in the directory.")
        exit(1)

    return latest_file


def take_action(feedback, watches):
    if scroll_maybe(feedback["rating"] * 1 / watches):
        logging.info("Scrolling to next video...")
        send_request(endpoints["next"])
        watches = 0
    else:
        watches += 1
        logging.info("Not scrolling")

def logger_config():
    # Set up basic logging configuration
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    logging.info("Application started")


if __name__ == "__main__":

    check_helpers()

    LLM = LLM()
    LLM.setIdentity(
        # "Suppose you are a very liberal stereotypical 18 year old girl watching instagram reels."
        "Suppose you are a stereotypical 16 year old guy from Kentucky watching instagram reels."
    )
    logging.info("LLM identity set")

    response = requests.post("http://localhost:4000/split")
    logging.info("First video split request sent")

    watches = 0

    while True:

        if watches:

            response = requests.post("http://localhost:4000/split")
            logging.info("Video split request sent")
            time.sleep(0.8)

            latest_file = get_clip()

            start_time = time.time()
            feedback = LLM.score(latest_file.resolve().as_posix())
            logging.info(f"Time to recieve: {time.time() - start_time}")

            print(feedback)

            take_action(feedback, watches)

        elif not watches:

            time.sleep(3)
            response = requests.post("http://localhost:4000/split")
            logging.info("Video split request sent")
            time.sleep(0.8)

            latest_file = get_clip()

            start_time = time.time()
            feedback = LLM.score(latest_file.resolve().as_posix())
            logging.info(f"Time to recieve: {time.time() - start_time}")

            take_action(feedback, watches)