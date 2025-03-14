import subprocess
import random
import time
import json
import shlex

# Constants
FILM_JSON_FILE = "film.json"
RTMP_URL = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"
OVERLAY_IMAGE = "overlay.png"

# HTTP Headers for iWantTFC
HEADERS = [
    "--http-header-fields=Accept: */*",
    "--http-header-fields=Accept-Encoding: gzip, deflate, br, zstd",
    "--http-header-fields=Accept-Language: en-US,en;q=0.9",
    "--http-header-fields=Cache-Control: no-cache",
    "--http-header-fields=Origin: https://www.iwanttfc.com",
    "--http-header-fields=Pragma: no-cache",
    "--http-header-fields=Referer: https://www.iwanttfc.com/",
    "--http-header-fields=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def load_movies(file_path):
    """Load movies from film.json."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def restream_movie(title, clearkey, mpd_url, overlay_image):
    """Runs MPV to restream an MPD link with ClearKey decryption and adds overlay via FFmpeg."""
    key_id, key_value = clearkey.split(":")  # Extract KID and Key
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    # Start MPV and output to a pipe
    mpv_command = [
        "mpv",
        "--no-cache",
        "--loop=no",
        "--profile=low-latency",
        "--stream-lavf-o=allowed_extensions=ALL",
        "--stream-lavf-o=protocol_whitelist=file,http,https,tcp,tls,crypto",
        "--demuxer-max-bytes=51200000",
        "--demuxer-max-back-bytes=51200000",
        "--input-ipc-server=/tmp/mpv-socket",
        "--stream-lavf-o=inputstream.adaptive",
        "--stream-lavf-o=inputstream.adaptive.manifest_type=mpd",
        "--stream-lavf-o=inputstream.adaptive.license_type=clearkey",
        f"--stream-lavf-o=inputstream.adaptive.license_key={key_id}:{key_value}",
        *HEADERS,  # Add HTTP headers
        "--o=-"  # Output raw video to pipe
    ]

    # FFmpeg pipeline to add overlay
    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-i", "-",  # Get input from MPV
        "-i", overlay_image,  # Overlay image
        "-filter_complex",
        f"[0:v][1:v]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
        "-c:v", "libx264",
        "-preset", "veryfast",
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

    # Run MPV and FFmpeg together
    mpv_proc = subprocess.Popen(mpv_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_proc = subprocess.Popen(ffmpeg_command, stdin=mpv_proc.stdout)

    # Wait for processes to finish
    ffmpeg_proc.wait()
    mpv_proc.wait()

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
