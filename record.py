import subprocess
import time
from datetime import datetime

# Options
FRAMERATE = 10
VIDEO_SIZE = "720x1280"
REC_X = 0
REC_Y = 0
REC_W = 896
REC_H = 504
output_dir = "./screen_recordings"

def record_screen_clip():

    output_file = f"{output_dir}/clip_%H-%M-%S.mp4"

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-video_size", VIDEO_SIZE, 
        "-framerate", str(FRAMERATE),         
        "-pix_fmt", "uyvy422",
        "-probesize", "5M",
        "-f", "avfoundation",             
        "-i", "4:1",                
        "-vf", f"crop={REC_H}:{REC_W}",
        "-preset", "ultrafast",
        "-crf", "40",
        "-tune", "zerolatency",
        "-r", "10",
        "-f", "segment",
        "-strftime", "1",
        "-segment_time", "3",
        "-force_key_frames", "expr:gte(t,n_forced*3)",  # Ensure a keyframe every 3 seconds
        "-reset_timestamps", "1",
        output_file
    ]

    # Run FFmpeg command
    subprocess.run(ffmpeg_command)

if __name__ == "__main__":
    record_screen_clip()

