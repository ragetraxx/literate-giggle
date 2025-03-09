import os
import json
import random
import shlex
import time
import subprocess

# RTMP Server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# File paths
overlay_path = "overlay.png"
intro_video = "channel.mp4"
movies_json = "movies.json"

def stream_video(video_url, overlay_text=None):
    """Streams a video and ensures FFmpeg restarts if it crashes."""
    video_url_escaped = shlex.quote(video_url)

    # FFmpeg Command: Apply overlay only if text is provided
    if overlay_text:
        overlay_path_escaped = shlex.quote(overlay_path)
        command = f"""
        ffmpeg -hide_banner -loglevel error -fflags +nobuffer -flags low_delay -strict experimental -re -i {video_url_escaped} \
        -i {overlay_path_escaped} -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1500k -maxrate 2000k -bufsize 4000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 96k -ar 44100 -f flv {shlex.quote(rtmp_url)}
        """
    else:
        # No overlay, just stream the video
        command = f"""
        ffmpeg -hide_banner -loglevel error -fflags +nobuffer -flags low_delay -strict experimental -re -i {video_url_escaped} \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1500k -maxrate 2000k -bufsize 4000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 96k -ar 44100 -f flv {shlex.quote(rtmp_url)}
        """

    print(f"Streaming: {video_url} (Overlay: {'Yes' if overlay_text else 'No'})")
    
    process = subprocess.Popen(command, shell=True)
    process.wait()  # Wait for FFmpeg to finish before continuing

while True:  # Main infinite loop
    try:
        # 1️⃣ Play `channel.mp4` ONCE before movies start
        if os.path.exists(intro_video):
            print("Playing channel.mp4 before the movie...")
            stream_video(intro_video)  # No overlay

        # 2️⃣ Load movies from JSON
        if not os.path.exists(movies_json):
            print("Error: movies.json not found! Retrying in 5 seconds...")
            time.sleep(5)
            continue  

        with open(movies_json, "r") as file:
            movies = json.load(file)

        # Filter valid movies
        valid_movies = [m for m in movies if "url" in m and "title" in m]

        if not valid_movies:
            print("No valid movies found in movies.json. Retrying in 5 seconds...")
            time.sleep(5)
            continue  

        # 3️⃣ Play movies continuously (RANDOM ORDER)
        while True:
            movie = random.choice(valid_movies)  # Select a random movie
            video_url = movie["url"]
            overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

            print(f"Playing: {movie['title']} ({video_url})")
            stream_video(video_url, overlay_text)  # With overlay

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Prevent infinite fast looping
