import requests
import json
import os

API_BASE_URL = "https://de1.api.radio-browser.info/json/stations"
JSON_FILE = "stations.json"

def fetch_radio_stations(country_code):
    """Fetch and filter radio stations strictly by country code."""
    url = f"{API_BASE_URL}/bycountrycodeexact/{country_code.upper()}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        stations = response.json()

        if not stations:
            print("\n❌ No stations found for this country.")
            return []

        return [
            {
                "name": s.get("name", "Unknown"),
                "url": s.get("url", ""),
                "logo": s.get("favicon", ""),
                "country": s.get("country", "Unknown"),
                "code": country_code.upper()  # Save country code for filtering
            }
            for s in stations if s.get("url")  # Ensure stream URL exists
        ]

    except requests.RequestException as e:
        print("Error fetching radio stations:", e)
        return []

def save_stations_to_json(stations, country_code):
    """Save or update stations in a JSON file."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Remove old entries from the same country
    data = [station for station in data if station["code"] != country_code.upper()]

    # Append new stations
    data.extend(stations)

    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"✅ {len(stations)} stations saved to {JSON_FILE}")

# === User Input ===
country_code = input("Enter country code (e.g., PH, US, GB): ").strip().upper()

if not country_code:
    print("❌ Please provide a country code.")
else:
    stations = fetch_radio_stations(country_code)
    if stations:
        save_stations_to_json(stations, country_code)
