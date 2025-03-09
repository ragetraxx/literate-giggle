import os
import shlex
import subprocess
import time

# RTMP Server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Audio Stream URL (Zeno.fm)
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"

# Overlay image
overlay_path = "overlay.png"

def stream_audio():
    """Streams an audio link continuously with an image overlay."""
    stream_escaped = shlex.quote(stream_url)
    overlay_escaped = shlex.quote(overlay_path)

    # Add headers to pretend FFmpeg is a web browser
    headers = "-headers 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'"

    command = f"""
    ffmpeg -re -loop 1 -i {overlay_escaped} {headers} -i {stream_escaped} \
    -vf "scale=1280:720" -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1500k -maxrate 2000k -bufsize 4000k \
    -c:a aac -b:a 128k -ar 44100 -f flv {shlex.quote(rtmp_url)}
    """

    print(f"Streaming: {stream_url} → {rtmp_url}")

    while True:
        process = subprocess.Popen(command, shell=True)
        process.wait()
        print("FFmpeg stopped. Restarting stream...")
        time.sleep(2)  # Prevent fast loop crashes

if __name__ == "__main__":
    stream_audio()
