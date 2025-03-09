import os
import json
import random
import shlex
import subprocess
import time

# RTMP Server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# File paths (Assuming movies.json is in the same directory as stream.py)
base_path = os.path.dirname(os.path.abspath(__file__))
overlay_path = os.path.join(base_path, "overlay.png")
intro_video = os.path.join(base_path, "channel.mp4")
movies_json = os.path.join(base_path, "movies.json")

def load_movies():
    """Loads movies from the JSON file and returns a list of valid entries."""
    if not os.path.exists(movies_json):
        print("Error: movies.json not found! Retrying in 5 seconds...")
        time.sleep(5)
        return []

    with open(movies_json, "r") as file:
        movies = json.load(file)

    valid_movies = [m for m in movies if "url" in m and "title" in m]
    if not valid_movies:
        print("No valid movies found in movies.json. Retrying in 5 seconds...")
        time.sleep(5)

    return valid_movies

def stream_video(video_url, overlay_text=None):
    """Streams a video with FFmpeg and restarts if it crashes."""
    video_url_escaped = shlex.quote(video_url)

    # FFmpeg Command: Apply overlay only if text is provided
    if overlay_text:
        overlay_path_escaped = shlex.quote(overlay_path)
        command = f"""
        ffmpeg -hide_banner -loglevel error -fflags +nobuffer -flags low_delay -rtbufsize 1M -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2 -i {video_url_escaped} \
        -i {overlay_path_escaped} -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1200k -maxrate 1500k -bufsize 3000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 96k -ar 44100 -f flv {shlex.quote(rtmp_url)}
        """
    else:
        command = f"""
        ffmpeg -hide_banner -loglevel error -fflags +nobuffer -flags low_delay -rtbufsize 1M -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2 -i {video_url_escaped} \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1200k -maxrate 1500k -bufsize 3000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 96k -ar 44100 -f flv {shlex.quote(rtmp_url)}
        """

    print(f"Streaming: {video_url} (Overlay: {'Yes' if overlay_text else 'No'})")

    while True:
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for FFmpeg to finish
        print("FFmpeg stopped. Restarting video...")
        time.sleep(2)  # Prevent infinite loop crashes

while True:
    try:
        # 1️⃣ Play `channel.mp4` ONCE before movies start
        if os.path.exists(intro_video):
            print("Playing channel.mp4 before the movies...")
            stream_video(intro_video)  # No overlay

        # 2️⃣ Load valid movies from `movies.json`
        movies = load_movies()
        if not movies:
            continue  # Retry if no valid movies found

        # 3️⃣ Play movies continuously (RANDOM ORDER)
        while True:
            movie = random.choice(movies)  # Select a random movie
            video_url = movie["url"]
            overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

            print(f"Playing: {movie['title']} ({video_url})")
            stream_video(video_url, overlay_text)  # With overlay

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Prevent infinite fast looping
