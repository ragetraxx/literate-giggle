import os
import shlex
import subprocess
import time

# RTMP Server URL
rtmp_url = "rtmp://ragetv:Blaze1110@ssh101.gia.tv/giatv-ragetv/ragetv"

# Video/audio source (replace this with your link)
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"  # Example: "https://example.com/stream.m3u8"

# Overlay image
overlay_path = "overlay.png"

def stream_video():
    """Streams a media link continuously with overlay."""
    video_url_escaped = shlex.quote(stream_url)
    overlay_escaped = shlex.quote(overlay_path)

    # FFmpeg Command with overlay
    command = f"""
    ffmpeg -re -i {video_url_escaped} -i {overlay_escaped} \
    -filter_complex "[1:v]scale2ref=w=iw:h=ih[ovr][base];[base][ovr]overlay=0:0" \
    -preset ultrafast -tune zerolatency -c:v libx264 -b:v 1500k -maxrate 2000k -bufsize 4000k -pix_fmt yuv420p -g 25 \
    -c:a aac -b:a 128k -ar 44100 -f flv {shlex.quote(rtmp_url)}
    """

    print(f"Streaming: {stream_url} → {rtmp_url}")

    while True:
        process = subprocess.Popen(command, shell=True)
        process.wait()
        print("FFmpeg stopped. Restarting stream...")
        time.sleep(2)  # Prevent fast loop crashes

if __name__ == "__main__":
    stream_video()
