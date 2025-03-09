import json
import random
import shlex
import subprocess
import time
import requests
import os

# RTMP Server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Raw GitHub URLs
movies_json_url = "https://raw.githubusercontent.com/ragetraxx/literate-giggle/main/movies.json"
intro_video_url = "https://raw.githubusercontent.com/ragetraxx/literate-giggle/main/channel.mp4"
overlay_url = "https://raw.githubusercontent.com/ragetraxx/literate-giggle/main/overlay.png"

def fetch_movies():
    """Fetches the latest movies.json from GitHub."""
    try:
        response = requests.get(movies_json_url)
        response.raise_for_status()
        movies = response.json()
        print(f"Fetched movies: {movies}")  # Debugging
        return [m for m in movies if "url" in m and "title" in m]
    except Exception as e:
        print(f"Error fetching movies.json: {e}")
        time.sleep(5)
        return []

def stream_video(video_url, overlay_text=None):
    """Streams a video using FFmpeg with headers to bypass 403 errors."""
    video_url_escaped = shlex.quote(video_url)

    # Add headers to pretend FFmpeg is a web browser
    headers = "-headers 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'"

    # FFmpeg Command
    if overlay_text:
        overlay_escaped = shlex.quote(overlay_url)
        command = f"""
        ffmpeg -hide_banner -loglevel error {headers} -re -i {video_url_escaped} \
        -i {overlay_escaped} -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 800k -maxrate 1000k -bufsize 2000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 64k -ar 32000 -f flv {shlex.quote(rtmp_url)}
        """
    else:
        command = f"""
        ffmpeg -hide_banner -loglevel error {headers} -re -i {video_url_escaped} \
        -preset ultrafast -tune zerolatency -c:v libx264 -b:v 800k -maxrate 1000k -bufsize 2000k -pix_fmt yuv420p -g 25 \
        -c:a aac -b:a 64k -ar 32000 -f flv {shlex.quote(rtmp_url)}
        """

    print(f"Streaming: {video_url} (Overlay: {'Yes' if overlay_text else 'No'})")

    while True:
        process = subprocess.Popen(command, shell=True)
        process.wait()
        print("FFmpeg stopped. Restarting video...")
        time.sleep(2)

while True:
    try:
        # 1️⃣ Play `channel.mp4` from GitHub before movies start
        print("Playing channel.mp4 before the movies...")
        stream_video(intro_video_url)  # No overlay

        # 2️⃣ Fetch movies from `movies.json`
        movies = fetch_movies()
        if not movies:
            continue  # Retry if no valid movies found

        # 3️⃣ Play movies continuously (RANDOM ORDER)
        while True:
            movie = random.choice(movies)  # Select a random movie
            video_url = movie["url"]
            overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")

            print(f"Playing: {movie['title']} ({video_url})")
            stream_video(video_url, overlay_text)  # With overlay

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
