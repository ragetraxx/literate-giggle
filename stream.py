import os
import json
import random
import time
import shlex
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# RTMP server
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragetv"

# Overlay image
overlay_path = "overlay.png"

# EPG file
epg_file = "epg.xml"

# Function to generate EPG XML
def generate_epg(schedule):
    tv = Element("tv")
    
    for movie in schedule:
        program = SubElement(tv, "programme", {
            "start": movie["start"],
            "stop": movie["stop"],
            "channel": "RageTV"
        })
        title = SubElement(program, "title", {"lang": "en"})
        title.text = movie["title"]
        desc = SubElement(program, "desc", {"lang": "en"})
        desc.text = f"Now Playing: {movie['title']}"

    # Save EPG as formatted XML
    xml_string = xml.dom.minidom.parseString(tostring(tv)).toprettyxml()
    with open(epg_file, "w", encoding="utf-8") as f:
        f.write(xml_string)

# Function to create a movie schedule
def create_schedule(movies):
    schedule = []
    start_time = datetime.utcnow()

    for movie in movies:
        duration = random.randint(60, 120)  # Simulated duration in minutes
        stop_time = start_time + timedelta(minutes=duration)

        schedule.append({
            "title": movie["title"],
            "url": movie["url"],
            "start": start_time.strftime("%Y%m%d%H%M%S %z"),
            "stop": stop_time.strftime("%Y%m%d%H%M%S %z"),
        })

        start_time = stop_time  # Set next start time

    return schedule

while True:  # Infinite loop
    try:
        # Load movies from JSON
        with open("movies.json", "r") as file:
            movies = json.load(file)

        # Filter valid movies
        valid_movies = [m for m in movies if "url" in m and "title" in m]

        if not valid_movies:
            print("No valid movies found.")
            time.sleep(5)
            continue

        # Create and save schedule
        schedule = create_schedule(valid_movies)
        generate_epg(schedule)

        for movie in schedule:
            video_url = movie["url"]
            overlay_text = movie["title"].replace(":", "\\:").replace("'", "\\'")  # Escape special characters

            # Safely escape paths
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

            # Run streaming
            os.system(command)

            # Short delay before selecting the next video
            time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)  # Delay before retrying
