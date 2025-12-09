import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "earthquakes_raw.csv")

def fetch_earthquake_data():
    """
    Fetches earthquake data for the last 24 hours.
    Returns a list of dictionaries.
    """
    # 1. Dynamic Time Window: Always fetch "Yesterday to Now"
    # This makes the script "idempotent" (safe to run daily)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%d"),
        "endtime": end_time.strftime("%Y-%m-%d"),
        "minmagnitude": "2.5" # Filter out noise (micro-quakes)
    }
    
    print(f"Fetching data from USGS ({params['starttime']} to {params['endtime']})...")
    
    try:
        response = requests.get(URL, params=params)
        response.raise_for_status() # Stop immediately if API is down
        data = response.json()
        
        features = data.get('features', [])
        print(f"Found {len(features)} earthquakes.")
        
        cleaned_data = []
        for feature in features:
            props = feature['properties']
            geometry = feature['geometry']
            
            # 2. Extract & Flat-Map: Convert nested JSON to a flat structure
            record = {
                "id": feature['id'],
                "magnitude": props['mag'],
                "place": props['place'],
                "time_utc": datetime.utcfromtimestamp(props['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "longitude": geometry['coordinates'][0],
                "latitude": geometry['coordinates'][1],
                "depth": geometry['coordinates'][2] # Depth in km
            }
            cleaned_data.append(record)
            
        return cleaned_data

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return []

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    quakes = fetch_earthquake_data()
    
    if quakes:
        df = pd.DataFrame(quakes)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"SUCCESS: Data saved to {OUTPUT_FILE}")
        print(df.head()) # Preview the first 5 rows
    else:
        print("WARNING: No data found or API failed.")