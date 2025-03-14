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
    "-headers", "Accept: */*",
    "-headers", "Accept-Encoding: gzip, deflate, br, zstd",
    "-headers", "Accept-Language: en-US,en;q=0.9",
    "-headers", "Cache-Control: no-cache",
    "-headers", "Origin: https://www.iwanttfc.com",
    "-headers", "Pragma: no-cache",
    "-headers", "Priority: u=1, i",
    "-headers", "Referer: https://www.iwanttfc.com/",
    "-headers", "Sec-Ch-Ua: \"Not/A)Brand\";v=\"99\", \"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\"",
    "-headers", "Sec-Ch-Ua-Mobile: ?0",
    "-headers", "Sec-Ch-Ua-Platform: Windows",
    "-headers", "Sec-Fetch-Dest: empty",
    "-headers", "Sec-Fetch-Mode: cors",
    "-headers", "Sec-Fetch-Site: same-site",
    "-headers", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def load_movies(file_path):
    """Load movies from film.json."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def restream_movie(title, clearkey, mpd_url, overlay_image):
    """Runs FFmpeg to restream an MPD link with ClearKey decryption and overlay."""
    key_id, key_value = clearkey.split(":")  # Extract KID and Key
    video_url_escaped = shlex.quote(mpd_url)
    overlay_path_escaped = shlex.quote(overlay_image)
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "32M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-allowed_extensions", "ALL",
        "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
        "-decryption_key", key_value,  # Apply ClearKey DRM decryption
        "-i", video_url_escaped,
        "-i", overlay_path_escaped,
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

    # Add HTTP headers
    command = HEADERS + command

    print(f"🎬 Now Streaming: {title}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Monitor FFmpeg output
    for line in process.stderr:
        print(line.decode(), end="")

    # Wait for the movie to finish
    process.wait()

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
