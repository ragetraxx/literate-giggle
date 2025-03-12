import os
import json
import random
import time
import shlex

# RTMP server
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Overlay image
overlay_path = "overlay.png"

# Files to track progress
index_file = "last_movie_index.txt"
played_movies_file = "played_movies.txt"

# Function to load movies
def load_movies():
    try:
        with open("movies.json", "r") as file:
            movies = json.load(file)

        valid_movies = [m for m in movies if "url" in m and "title" in m]
        if not valid_movies:
            print("No valid movies found in JSON file.")
            return []
        return valid_movies

    except Exception as e:
        print(f"Failed to load movies.json: {e}")
        return []

# Function to get last played index
def get_last_movie_index():
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as file:
                return int(file.read().strip())
        except:
            return 0
    return 0

# Function to save last played index
def save_last_movie_index(index):
    with open(index_file, "w") as file:
        file.write(str(index))

# Function to get played movies
def get_played_movies():
    if os.path.exists(played_movies_file):
        try:
            with open(played_movies_file, "r") as file:
                return set(file.read().splitlines())
        except:
            return set()
    return set()

# Function to save played movie
def save_played_movie(title):
    with open(played_movies_file, "a") as file:
        file.write(title + "\n")

while True:
    try:
        movies = load_movies()
        if not movies:
            print("No valid movies available. Retrying in 10 seconds...")
            time.sleep(10)
            continue

        played_movies = get_played_movies()
        available_movies = [m for m in movies if m["title"] not in played_movies]

        if not available_movies:  # If all movies have been played, reset the list
            print("All movies played. Resetting the list...")
            with open(played_movies_file, "w") as file:
                file.write("")
            available_movies = movies

        # Select a random movie from unplayed movies
        movie = random.choice(available_movies)
        video_url = movie["url"]
        overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")

        # Escape paths
        video_url_escaped = shlex.quote(video_url)
        overlay_path_escaped = shlex.quote(overlay_path)

        # FFmpeg command
        command = f"""
        ffmpeg -re -i {video_url_escaped} -i {overlay_path_escaped} \
        -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -c:v libx264 -preset veryfast -b:v 2000k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 \
        -c:a aac -b:a 192k -ar 48000 -f flv {shlex.quote(rtmp_url)}
        """

        print(f"Streaming: {movie['title']} ({video_url})")

        # Save progress
        save_last_movie_index(movies.index(movie))
        save_played_movie(movie["title"])

        # Run FFmpeg streaming
        os.system(command)

        # Short delay before next video
        time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)  # Retry delay
