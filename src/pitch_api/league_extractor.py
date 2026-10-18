import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import pandas as pd
import json
import requests


#get the league ids from the API by sending a request
##only need to do this once

project_dir = Path(__file__).resolve().parents[2]

load_dotenv(project_dir / '.env')
api_key = os.getenv('api_key_pitch')

#print("ENV exists:", (project_dir / ".env").exists())
#print("API key loaded:", bool(api_key))
#print("API key length:", len(api_key) if api_key else 0)

url = "https://api.pitchapi.dev/v1/leagues"

headers = {
    "X-API-KEY": api_key
}

file_path = project_dir / 'data' / 'pitch_api_data' / 'raw_data' / 'leagues.json'

if file_path.exists():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
#if the file already exists, load the data from it instead of making a new API request

else:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
 #make an API request, with a 30-second timeout to avoid waiting indefinitely

    data = response.json()
#convert the response to a python dictionary

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


leagues = data['data']['leagues']
#get the list of leagues from the API response, which is nested under 'data' and then 'leagues'

league_ids = {}
#create an empty dictionary to store the league names and their corresponding IDs

for league in leagues:
    league_ids[league['name']] = league['id']
#extract the league names and their corresponding IDs from the API response and store them in a dictionary

leagues_df = pd.DataFrame(league_ids.items(), columns=['League Name', 'League ID'])

csv_path = project_dir / 'data' / 'pitch_api_data' / 'processed_data' / 'leagues.csv'

csv_path.parent.mkdir(parents=True, exist_ok=True)
#makes sure progress is saved

leagues_df.to_csv(csv_path, index=False)
#convert df to csv



#print("API key found:", bool(api_key))
#print("Status:", response.status_code)
#print("Response:", response.text[:500])