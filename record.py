import subprocess
import time
from datetime import datetime

FRAMERATE = 10
VIDEO_SIZE = "1280x720"

# Directory to save clips
output_dir = "./screen_recordings"

# Function to record a 3-second screen video
def record_screen_clip():

    # Create a unique filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/clip_{timestamp}.mp4"

    # FFmpeg command to capture a 3-second screen clip
    ffmpeg_command = [
        "ffmpeg",
        "-y",  # Overwrite output file if exists
        "-video_size", VIDEO_SIZE,  # Set your screen resolution here
        "-framerate", str(FRAMERATE),          # Frames per second
        "-pix_fmt", "uyvy422",
        "-probesize", "10M",
        "-f", "avfoundation",             # Screen capture for Linux; use "gdigrab" on Windows or "avfoundation" on macOS
        "-i", "4:1",                # Video : Audio
        "-vf", "crop=800:600:100:100",
        "-t", "3",                   # Duration of the clip (3 seconds)
        "-preset", "ultrafast",
        "-crf", "28",
        output_file
    ]

    # Run FFmpeg command
    subprocess.run(ffmpeg_command)

    print(f"Saved clip: {output_file}")


if __name__ == "__main__":
    while True:
        record_screen_clip()
        time.sleep(3)  # Wait 3 seconds before the next clip

