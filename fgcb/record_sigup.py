from flask import Flask, request
import subprocess
import os
import logging
import time
import threading
import signal
import sys

app = Flask(__name__)

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)

# Directory for saving screen recordings
output_directory = "../screen_recordings/"
os.makedirs(output_directory, exist_ok=True)

# Global variable to hold the ffmpeg process
ffmpeg_process = None
lock = threading.Lock()

# Function to start the ffmpeg process
def start_ffmpeg():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_directory, f"clip_{timestamp}.mp4")
    
    ffmpeg_command = [
        "ffmpeg", "-y",
        "-video_size", "648x1152",
        "-framerate", "10",
        "-pix_fmt", "uyvy422",
        "-probesize", "5M",
        "-f", "avfoundation", "-i", "3:0",
        "-vf", "crop=720:1280,setpts=N/10/TB",  # Adjust to 10 to match framerate
        "-preset", "ultrafast",
        "-crf", "30",
        "-tune", "zerolatency",
        "-r", "10",
        "-f", "segment",
        "-strftime", "1",
        "-reset_timestamps", "1",
        output_file
    ]

    logging.info(f"Starting ffmpeg with command: {' '.join(ffmpeg_command)}")
    
    # Start the ffmpeg process and capture stdout and stderr
    process = subprocess.Popen(
        ffmpeg_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    return process

# Thread function to run ffmpeg
def run_ffmpeg():
    global ffmpeg_process

    while True:
        with lock:
            if ffmpeg_process is None:
                ffmpeg_process = start_ffmpeg()

        # Wait for the ffmpeg process to exit and log its output
        stdout, stderr = ffmpeg_process.communicate()  # Wait for it to finish
        if stdout:
            logging.info(f"ffmpeg output: {stdout.decode().strip()}")
        if stderr:
            logging.error(f"ffmpeg error: {stderr.decode().strip()}")

        # Log if the ffmpeg process exits unexpectedly
        logging.warning("ffmpeg process has exited. Restarting...")
        time.sleep(1)  # Brief sleep before restarting

# Start the ffmpeg process in a separate thread
ffmpeg_thread = threading.Thread(target=run_ffmpeg, daemon=True)
ffmpeg_thread.start()

@app.route('/split', methods=['POST'])
def split_segment():
    global ffmpeg_process
    
    with lock:
        if ffmpeg_process and ffmpeg_process.poll() is None:  # Check if it's running
            logging.info("Terminating current ffmpeg process.")
            ffmpeg_process.terminate()
            ffmpeg_process.wait()  # Wait for it to fully close
            logging.info("Current ffmpeg process terminated.")
        
        # Start a new ffmpeg process for the next segment
        ffmpeg_process = start_ffmpeg()
        logging.info("New segment started.")

    return "New segment started", 200

@app.route('/status', methods=['GET'])
def status():
    return {"status": "running"}

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global ffmpeg_process
    logging.info("Shutting down the server...")
    
    with lock:
        if ffmpeg_process and ffmpeg_process.poll() is None:
            ffmpeg_process.terminate()
            ffmpeg_process.wait()  # Ensure it closes completely

    shutdown_function = request.environ.get('werkzeug.server.shutdown')
    if shutdown_function:
        shutdown_function()
    logging.info("Server has been shut down.")
    return 'Server shutting down...', 200

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logging.info("Signal received, shutting down...")
    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.terminate()
        ffmpeg_process.wait()  # Ensure it closes completely
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
