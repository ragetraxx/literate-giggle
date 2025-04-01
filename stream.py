import os
import json
import subprocess
import time

# Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")  # Get RTMP_URL from environment
OVERLAY = os.path.abspath("overlay.png")
MAX_RETRIES = 3
RETRY_DELAY = 60

# Check if RTMP_URL is set
if not RTMP_URL:
    print("\u274c ERROR: RTMP_URL environment variable is NOT set! Check your configuration.")
    exit(1)

# Ensure required files exist
if not os.path.exists(PLAY_FILE):
    print(f"\u274c ERROR: {PLAY_FILE} not found!")
    exit(1)
if not os.path.exists(OVERLAY):
    print(f"\u274c ERROR: Overlay image '{OVERLAY}' not found!")
    exit(1)

def load_movies():
    """Load movies from play.json."""
    try:
        with open(PLAY_FILE, "r") as f:
            movies = json.load(f)
            return movies if movies else print("\u274c ERROR: play.json is empty!") or []
    except json.JSONDecodeError:
        print("\u274c ERROR: Failed to parse play.json! Check for syntax errors.")
        return []

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"\u274c ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\\:").replace("'", r"\\'").replace('"', r'\\"')

    command = [
        "ffmpeg", "-re", "-fflags", "+genpts",
        "-rtbufsize", "8M", "-probesize", "32M", "-analyzeduration", "32M",
        "-i", url, "-i", OVERLAY,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30",
        "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0",  # ✅ Constrained Baseline
        "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "18",
        "-maxrate", "5000k", "-bufsize", "6000k", "-pix_fmt", "yuv420p",
        "-g", "48",  # ✅ Lower keyframe interval
        "-r", "23.976",  # ✅ Match film standard
        "-c:a", "aac", "-profile:a", "aac_low", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", "-f", "flv", RTMP_URL,
        "-loglevel", "error"
    ]

    print(f"\ud83c\udfa5 Now Streaming: {title}")
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            print(line, end="")
        process.wait()
    except Exception as e:
        print(f"\u274c ERROR: FFmpeg failed for '{title}' - {str(e)}")

def main():
    """Main function to stream all movies in sequence."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()
        if not movies:
            retry_attempts += 1
            print(f"\u274c ERROR: No movies available! Retrying ({retry_attempts}/{MAX_RETRIES}) in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            continue

        retry_attempts = 0  # Reset retry counter
        while True:
            for movie in movies:
                stream_movie(movie)
                print("\ud83d\udd04 Movie ended. Playing next movie...")
            print("\ud83d\udd04 All movies played, restarting from the beginning...")
    
    print("\u274c ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
