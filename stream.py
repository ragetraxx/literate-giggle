import os
import json
import time
import shlex
import logging
import random
import subprocess

# Configure logging
logging.basicConfig(filename="stream.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# RTMP server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Overlay image path
overlay_path = "overlay.png"

# Files for saving state
index_file = "last_movie_index.txt"
movies_file = "movies.json"

# Load movies from JSON
def load_movies():
    try:
        with open(movies_file, "r") as file:
            movies = json.load(file)
        return [m for m in movies if "url" in m and "title" in m]
    except Exception as e:
        logging.error(f"Failed to load {movies_file}: {e}")
        return []

# Get movie duration using FFmpeg
def get_movie_duration(video_url):
    try:
        cmd = ["ffprobe", "-i", video_url, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return int(float(result.stdout.strip())) if result.stdout.strip() else None
    except Exception as e:
        logging.error(f"Failed to get duration for {video_url}: {e}")
        return None

# Save the last played state
def save_movie_state(movie_index, elapsed_time, played_movies):
    with open(index_file, "w") as file:
        file.write(f"{movie_index},{elapsed_time},{','.join(map(str, played_movies))}")

# Load the last played state
def load_movie_state():
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as file:
                data = file.read().strip().split(",")
                movie_index = int(data[0])
                elapsed_time = int(data[1])
                played_movies = list(map(int, data[2:])) if len(data) > 2 else []
                return movie_index, elapsed_time, played_movies
        except:
            return -1, 0, []  # Reset state if file is corrupted
    return -1, 0, []  # No saved state, start fresh

# Check if movies.json was updated
def check_movies_update(current_movies):
    new_movies = load_movies()
    if new_movies != current_movies:
        logging.info("movies.json was updated. Reloading movies...")
        return new_movies
    return current_movies

# Initial Load
movies = load_movies()
movie_index, elapsed_time, played_movies = load_movie_state()
last_modified_time = os.path.getmtime(movies_file) if os.path.exists(movies_file) else 0

# Ensure played_movies is valid
played_movies = [i for i in played_movies if i < len(movies)]

# Function to get next random movie that hasn't been played yet
def get_next_movie():
    global played_movies
    if len(played_movies) == len(movies):  # Reset when all movies are played
        played_movies = []
    available_movies = [i for i in range(len(movies)) if i not in played_movies]
    return random.choice(available_movies)

# If script restarted, resume last movie if available
if movie_index == -1 or movie_index >= len(movies):
    movie_index = get_next_movie()
    elapsed_time = 0

while True:
    try:
        # Check for updates in movies.json
        if os.path.exists(movies_file):
            modified_time = os.path.getmtime(movies_file)
            if modified_time > last_modified_time:
                last_modified_time = modified_time
                movies = check_movies_update(movies)

        if not movies:
            logging.warning("No valid movies available. Retrying in 10 seconds...")
            time.sleep(10)
            movies = load_movies()
            continue

        # Get next random movie that hasn't been played yet
        movie_index = get_next_movie()
        played_movies.append(movie_index)  # Mark as played
        movie = movies[movie_index]
        video_url = movie["url"]
        overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")

        # Escape paths
        video_url_escaped = shlex.quote(video_url)
        overlay_path_escaped = shlex.quote(overlay_path)

        # Get movie duration
        duration = get_movie_duration(video_url)
        if duration is None:
            logging.warning(f"Skipping {movie['title']} due to missing duration.")
            continue

        # FFmpeg command with resume from last saved time
        command = f"""
        ffmpeg -re -ss {elapsed_time} -i {video_url_escaped} -i {overlay_path_escaped} \
        -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20" \
        -c:v libx264 -preset veryfast -b:v 2000k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 \
        -c:a aac -b:a 192k -ar 48000 -f flv {shlex.quote(rtmp_url)}
        """

        logging.info(f"Streaming: {movie['title']} ({video_url}) from {elapsed_time}s")

        # Run streaming process
        process = subprocess.Popen(command, shell=True)
        start_time = time.time()

        # Monitor streaming process
        while process.poll() is None:
            time.sleep(10)
            elapsed_time = int(time.time() - start_time)
            save_movie_state(movie_index, elapsed_time, played_movies)

        logging.info(f"Finished streaming: {movie['title']}")

        # Reset elapsed time after movie completes
        elapsed_time = 0
        save_movie_state(movie_index, elapsed_time, played_movies)

        # Short delay before selecting the next video
        time.sleep(3)

    except Exception as e:
        logging.error(f"Error: {e}")
        time.sleep(10)  # Delay before retrying
