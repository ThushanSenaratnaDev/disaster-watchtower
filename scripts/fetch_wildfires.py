import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 1. Load the secret from .env
load_dotenv()
API_KEY = os.getenv("NASA_API_KEY")

# Configuration
# Source: VIIRS_SNPP_NRT (Visible Infrared Imaging Radiometer Suite)
# It detects smaller fires than older satellites like MODIS.
BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
SOURCE = "VIIRS_SNPP_NRT"
AREA = "world"
DAYS = 1

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wildfires_raw.csv")

def fetch_wildfire_data():
    """
    Fetches global wildfire data for the last 24 hours.
    Saves directly to CSV.
    """
    if not API_KEY:
        print("ERROR: NASA_API_KEY not found in .env file.")
        return

    # Construct the API URL
    # Format: /api/area/csv/[MAP_KEY]/[SOURCE]/[AREA_COORDINATES]/[DAY_RANGE]
    url = f"{BASE_URL}/{API_KEY}/{SOURCE}/{AREA}/{DAYS}"
    
    print(f"Fetching wildfire data from NASA FIRMS ({SOURCE})...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # The API returns raw CSV text.
        # We save it directly to our 'raw' data layer.
        data_text = response.text
        
        # Check if we actually got data (headers usually come first)
        if "latitude,longitude" not in data_text and "No Data" in data_text:
             print("No fires detected or API limit reached.")
             return

        # Write to file
        with open(OUTPUT_FILE, "w") as f:
            f.write(data_text)
            
        # Count lines to give feedback (subtract 1 for header)
        line_count = len(data_text.strip().split("\n")) - 1
        print(f"SUCCESS: Saved {line_count} fire records to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fetch_wildfire_data()