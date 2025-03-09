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

def stream_video(video_url, overlay_text):
    """Streams a video to RTMP with an overlay, optimized for low latency."""
    while True:  # Restart if FFmpeg crashes
        try:
            video_url_escaped = shlex.quote(video_url)
            overlay_path_escaped = shlex.quote(overlay_path)

            command = f"""
            ffmpeg -hide_banner -loglevel error -fflags +genpts -re -i {video_url_escaped} \
            -i {overlay_path_escaped} -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
            -preset ultrafast -tune zerolatency -c:v libx264 -b:v 3000k -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -g 50 \
            -c:a aac -b:a 128k -ar 44100 -f flv -flvflags no_duration_filesize {shlex.quote(rtmp_url)}
            """

            print(f"Streaming: {overlay_text} ({video_url})")
            subprocess.run(command, shell=True, check=True)

        except subprocess.CalledProcessError:
            print(f"FFmpeg crashed while streaming {overlay_text}, restarting...")
            time.sleep(2)  # Short delay before restarting

while True:  # Infinite loop
    try:
        # Check if movies.json exists
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

        # Select a random movie
        movie = random.choice(valid_movies)
        video_url = movie["url"]
        overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

        # 1️⃣ Play channel.mp4 first (only if it exists)
        if os.path.exists(intro_video):
            print("Playing channel.mp4 before the movie...")
            stream_video(intro_video, "Welcome to RageTV")

        # 2️⃣ Play the selected movie from movies.json
        stream_video(video_url, overlay_text)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Prevent infinite fast looping
