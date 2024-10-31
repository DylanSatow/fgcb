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

    LLM = LLM(
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
