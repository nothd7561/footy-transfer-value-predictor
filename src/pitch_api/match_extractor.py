import os
import pandas as pd
from pathlib import Path
import json
import requests
from dotenv import load_dotenv, find_dotenv
import sys

###extract the matches from the league id


file_dir = Path(__file__).resolve().parents[2]
#get the overall path of the file

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON, MATCH_SEASON, COUNTRY_CODE

input_file_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / 'leagues.json'
#path for the json raw file, which contains the league names and their corresponding IDs

load_dotenv(file_dir / '.env')
api_key = os.getenv('api_key_pitch')
#acquire api key from the .env file, which is not included in the repo for security reasons

if not api_key:
    raise ValueError("PitchAPI key not found in .env")

with open(input_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    #load the json file into a python dictionary

leagues = data['data']['leagues']
for league in leagues:
    if league['name'] == LEAGUE_NAME and league['country_code'] == COUNTRY_CODE:
        league_id = league['id']
        break

if league_id is None:
    raise ValueError(f"League not found: {LEAGUE_NAME}")
#fallback if the naming convention is wrong


url = f'https://api.pitchapi.dev/v1/leagues/{league_id}/matches'

headers = {'X-API-KEY': api_key}
params = {'season': MATCH_SEASON}

save_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / f'matches_{LEAGUE_NAME}_{SEASON}.json'
#establish the path for saving the matches data, replacing '/' with '-' in the season string to avoid issues with file naming
#there might be issues since / is used for splitting paths

if save_path.exists():
    with open(save_path, 'r', encoding='utf-8') as f:
        match_data = json.load(f)
    #if the file already exists, load the data from it instead of making a new API request
    print('File found, already exists, lets load the data')
else:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print("Status:", response.status_code)
    print("Response:", response.text)
    print("URL:", response.url)
    response.raise_for_status()

    match_data = response.json()
    #convert the response to a python dictionary

    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(match_data, f, indent=4)

    print('File not found, lets fetch the data')

print(match_data.keys())

