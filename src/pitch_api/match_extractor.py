import os
import pandas as pd
from pathlib import Path
import json
import requests
from dotenv import load_dotenv, find_dotenv

###extract the matches from the league id

file_dir = Path(__file__).resolve().parents[2]
#get the overall path of the file

input_file_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / 'leagues.json'
#path for the json raw file, which contains the league names and their corresponding IDs

load_dotenv(file_dir / '.env')
api_key = os.getenv('api_key_pitch')
#acquire api key from the .env file, which is not included in the repo for security reasons

with open(input_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    #load the json file into a python dictionary

leagues = data['data']['leagues']
for league in leagues:
    if league['name'] == 'Premier League':
        league_id = league['id']

season = '2025'
#changed from 2025/2026

url = f'https://api.pitchapi.dev/v1/leagues/{league_id}/matches'

headers = {'X-API-KEY': api_key}
params = {'season': season}

save_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / f'matches_{league_id}_{season.replace("/", "-")}.json'
#establish the path for saving the matches data, replacing '/' with '-' in the season string to avoid issues with file naming
#there might be issues since / is used for splitting paths

if save_path.exists():
    with open(save_path, 'r', encoding='utf-8') as f:
        match_data = json.load(f)
    #if the file already exists, load the data from it instead of making a new API request
    print('File found, already exists, lets load the data')
else:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    #print("Status:", response.status_code)
    #print("Response:", response.text)
    #print("URL:", response.url)
    response.raise_for_status()

    match_data = response.json()
    #convert the response to a python dictionary

    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(match_data, f, indent=4)

    print('File not found, lets fetch the data')

print(match_data.keys())

