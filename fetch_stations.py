import requests
import json
import os

API_BASE_URL = "https://de1.api.radio-browser.info/json/stations"
JSON_FILE = "stations.json"

def fetch_radio_stations(country_code):
    """Fetch and filter radio stations by country code."""
    url = f"{API_BASE_URL}/bycountrycodeexact/{country_code.upper()}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        stations = response.json()

        if not stations:
            print("\n🚫 No stations found for this country.")
            return []

        return [
            {
                "name": s.get("name", "Unknown"),
                "url": s.get("url", ""),
                "logo": s.get("favicon", ""),
                "country": s.get("country", "Unknown"),
                "code": country_code.upper()
            }
            for s in stations if s.get("url")  # Ensure stream URL exists
        ]

    except requests.RequestException as e:
        print("Error fetching radio stations:", e)
        return []

def save_to_json(stations):
    """Save or update stations in JSON file."""
    existing_data = []
    
    # Load existing data if JSON file exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []

    # Create a dictionary for quick lookup of existing stations
    station_dict = {s["name"]: s for s in existing_data}

    # Update or append new stations
    for station in stations:
        station_dict[station["name"]] = station  # Overwrite if exists

    # Save updated list back to JSON
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(list(station_dict.values()), file, indent=4)
    
    print(f"\n✅ Stations saved to {JSON_FILE}")

def display_stations():
    """Display saved stations from JSON file."""
    if not os.path.exists(JSON_FILE):
        print("\n🚫 No saved stations found.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        try:
            stations = json.load(file)
            if not stations:
                print("\n🚫 No saved stations found.")
                return
            
            print("\n📻 Saved Radio Stations 📻")
            for index, station in enumerate(stations, 1):
                print(f'{index}. {station["name"]} - {station["url"]} - {station["logo"]}')
        except json.JSONDecodeError:
            print("\n🚫 Error reading stations.json")

# === User Input ===
country_code = input("Enter country code (e.g., PH, US, GB): ").strip().upper()

if not country_code:
    print("🚫 Please provide a country code.")
else:
    stations = fetch_radio_stations(country_code)
    if stations:
        save_to_json(stations)
        display_stations()