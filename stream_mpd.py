import subprocess
import random
import time
import json
import shlex

# Constants
FILM_JSON_FILE = "film.json"
RTMP_URL = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"
OVERLAY_IMAGE = "overlay.png"

def load_movies(file_path):
    """Load movies from film.json."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def restream_movie(title, clearkey, mpd_url, overlay_image):
    """Runs MPV with inputstream.adaptive and pipes it into FFmpeg for RTMP streaming."""
    
    # Extract Key ID and Key
    kid, key = clearkey.split(":")

    # Escape special characters for FFmpeg
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    # MPV Command to Play & Decrypt the MPD Stream
    mpv_command = [
        "mpv",
        "--no-cache",
        "--stream-buffer-size=64M",
        "--stream-lavf-o=protocol_whitelist=file,http,https,tcp,tls,crypto",
        f"--demuxer-lavf-o=inputstream.adaptive.license_type=org.w3.clearkey",
        f"--demuxer-lavf-o=inputstream.adaptive.license_key={kid}:{key}",
        mpd_url,
        "--no-video",  # Pass video to FFmpeg instead
        "--vo=null",
        "--ao=pcm",
        "--af=format=s16le",
        "--audio-device=pipe:1"
    ]

    # FFmpeg Command to Overlay Text and Stream to RTMP
    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "32M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-i", "-",  # Read decrypted video from MPV
        "-i", overlay_image,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "film",
        "-b:v", "3000k",
        "-maxrate", "3500k",
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title}")

    # Run MPV and FFmpeg in a pipeline
    with subprocess.Popen(mpv_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as mpv_proc:
        with subprocess.Popen(ffmpeg_command, stdin=mpv_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as ffmpeg_proc:
            ffmpeg_proc.wait()  # Wait for the movie to finish

def main():
    """Continuously pick and stream movies from film.json."""
    movies = load_movies(FILM_JSON_FILE)
    if not movies:
        print("⚠️ No valid movies found in film.json")
        return

    while True:
        movie = random.choice(movies)
        restream_movie(movie["title"], movie["clearkey"], movie["mpd"], OVERLAY_IMAGE)
        print("🎬 Movie ended. Picking a new one...")
        time.sleep(5)  # Small delay before starting the next movie

if __name__ == "__main__":
    main()
