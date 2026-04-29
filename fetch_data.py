import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

API_URL = "https://cricket-api-free-data.p.rapidapi.com/cricket-schedule" 

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "cricket-api-free-data.p.rapidapi.com"
}

CACHE_FILE = "cached_sports_data.json"

def get_sports_data():
    if os.path.exists(CACHE_FILE):
        print("📂 FOUND LOCAL CACHE: Loading data from your hard drive to save API limits...")
        with open(CACHE_FILE, 'r') as file:
            data = json.load(file)
            return data
            
    else:
        print("🌐 NO CACHE FOUND: Connecting to the internet to fetch live API data...")
        response = requests.get(API_URL, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            with open(CACHE_FILE, 'w') as file:
                json.dump(data, file, indent=4)
            print("✅ SUCCESS: Data downloaded and saved to cache!")
            return data
        else:
            print(f"❌ ERROR: API request failed with status code {response.status_code}")
            return None

sports_data = get_sports_data()

if sports_data:
    print("\n--- PREVIEW OF DATA ---")
    print(str(sports_data)[:500] + "...\n")