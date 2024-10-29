import subprocess
import time
from datetime import datetime

FRAMERATE = 10
VIDEO_SIZE = "896x504"
REC_X = 0
REC_Y = 0
REC_W = 896
REC_H = 504

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
        "-probesize", "5M",
        "-f", "avfoundation",             # Screen capture for Linux; use "gdigrab" on Windows or "avfoundation" on macOS
        "-i", "4:1",                # Video : Audio
        # "-vf", f"crop={REC_H}:{REC_W}:{REC_X}:{REC_Y}",
        "-vf", f"crop={REC_H}:{REC_W}",
        # "-t", "3",                   # Duration of the clip (3 seconds)
        "-preset", "ultrafast",
        "-crf", "40",
        "-tune", "zerolatency",
        "-r", "10",
        "-f", "segment",
        "-strftime", "1",
        "-segment_time", "3",
        "-force_key_frames", "expr:gte(t,n_forced*3)",  # Ensure a keyframe every 3 seconds
        "-reset_timestamps", "1",
        f"{output_dir}/clip_%H-%M-%S.mp4"
    ]

    # Run FFmpeg command
    subprocess.run(ffmpeg_command)

    print(f"Saved clip: {output_file}")


if __name__ == "__main__":
    record_screen_clip()

