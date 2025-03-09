import os
import json
import random
import shlex

# RTMP server
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Overlay image
overlay_path = "overlay.png"

# Intro video
intro_video = "channel.mp4"

def stream_video(video_url, overlay_text):
    """Streams a video to RTMP with overlay text."""
    try:
        # Escape paths safely
        video_url_escaped = shlex.quote(video_url)
        overlay_path_escaped = shlex.quote(overlay_path)

        # FFmpeg command
        command = f"""
        ffmpeg -re -i {video_url_escaped} -i {overlay_path_escaped} \
        -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -c:v libx264 -preset veryfast -b:v 3000k -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -g 50 \
        -c:a aac -b:a 128k -ar 44100 -f flv {shlex.quote(rtmp_url)}
        """
        
        print(f"Streaming: {overlay_text} ({video_url})")
        os.system(command)

    except Exception as e:
        print(f"Error streaming {overlay_text}: {e}")

while True:  # Infinite loop
    try:
        # Load movies from JSON
        with open("movies.json", "r") as file:
            movies = json.load(file)

        # Filter out valid movies
        valid_movies = [m for m in movies if "url" in m and "title" in m]

        if not valid_movies:
            print("No valid movies found in JSON file. Retrying...")
            continue  # No sleep, retry instantly

        # Select a random movie
        movie = random.choice(valid_movies)
        video_url = movie["url"]
        overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

        # Play channel.mp4 before the movie
        if os.path.exists(intro_video):
            print("Playing channel.mp4 before movie...")
            stream_video(intro_video, "Welcome to RageTV")

        # Play the selected movie
        stream_video(video_url, overlay_text)

    except Exception as e:
        print(f"Error: {e}")
        continue  # Retry immediately 
