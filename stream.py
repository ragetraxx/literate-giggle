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
    """Streams a video and ensures it resumes playback if it buffers."""
    try:
        video_url_escaped = shlex.quote(video_url)

        # FFmpeg Command: If overlay text is provided, apply overlay
        if overlay_text:
            overlay_path_escaped = shlex.quote(overlay_path)
            command = f"""
            ffmpeg -hide_banner -loglevel error -re -stream_loop -1 -i {video_url_escaped} \
            -i {overlay_path_escaped} -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
            -preset ultrafast -tune zerolatency -c:v libx264 -b:v 3000k -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -g 50 \
            -c:a aac -b:a 128k -ar 44100 -f flv {shlex.quote(rtmp_url)}
            """
        else:
            # No overlay, just stream the video
            command = f"""
            ffmpeg -hide_banner -loglevel error -re -stream_loop -1 -i {video_url_escaped} \
            -preset ultrafast -tune zerolatency -c:v libx264 -b:v 3000k -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -g 50 \
            -c:a aac -b:a 128k -ar 44100 -f flv {shlex.quote(rtmp_url)}
            """

        print(f"Streaming: {video_url} (Overlay: {'Yes' if overlay_text else 'No'})")

        # Run FFmpeg process and keep it running
        while True:
            process = subprocess.Popen(command, shell=True)
            process.wait()

            # If FFmpeg stops unexpectedly, restart it
            print(f"FFmpeg stopped while streaming {video_url}. Restarting...")
            time.sleep(2)

    except Exception as e:
        print(f"Error streaming {video_url}: {e}")
        time.sleep(2)  # Short delay before retrying

while True:  # Infinite loop
    try:
        # 1️⃣ Play `channel.mp4` first WITHOUT overlay
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

        # 3️⃣ Play movies continuously (WITH overlay)
        while True:
            movie = random.choice(valid_movies)
            video_url = movie["url"]
            overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

            print(f"Playing: {movie['title']} ({video_url})")
            stream_video(video_url, overlay_text)  # With overlay

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Prevent infinite fast looping
