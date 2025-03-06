import os
import requests
import json

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
                "country": s.get("country", "Unknown")
            }
            for s in stations if s.get("url")  # Ensure stream URL exists
        ]

    except requests.RequestException as e:
        print("Error fetching radio stations:", e)
        return []

def save_to_json(stations):
    """Save or update radio stations in JSON format."""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Remove duplicate entries for the same station
    new_data = {s["url"]: s for s in existing_data}
    for station in stations:
        new_data[station["url"]] = station

    # Save updated JSON file
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(list(new_data.values()), file, indent=4)

    print(f"\n✅ Stations saved to {JSON_FILE}")

# === GitHub Actions Fix: Get country code from environment variable ===
country_code = os.getenv("COUNTRY_CODE", "US")  # Default to "US"

if not country_code:
    print("🚫 COUNTRY_CODE environment variable is missing.")
else:
    stations = fetch_radio_stations(country_code)
    if stations:
        save_to_json(stations)
