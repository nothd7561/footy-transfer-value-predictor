import os
import json
import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import sys

###get the player stats from each match, using the match ids we got from the league extraction

file_dir = Path(__file__).resolve().parents[2]
#establish file path

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON, MATCH_SEASON

input_file_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / f'{MATCH_SEASON}'/ f'matches_{LEAGUE_NAME}_{SEASON}.json'

with open(input_file_path, 'r', encoding='utf-8') as f:
    match_data = json.load(f)
    #load the json file into a python dictionary

match_ids = []
#create empty list to store match ids

league_matches = match_data['data']['matches']
for match in league_matches:
    match_ids.append(str(match['id']))
    #get a list of all the match ids so that we can loop through them for the stats request

load_dotenv(file_dir / '.env')
api_key = os.getenv('api_key_pitch')
#load the api key from the env file

if not api_key:
     raise ValueError('No API key detected, freezing script')

headers = {'X-API-KEY' : api_key}

save_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / f'{MATCH_SEASON}' / f'player_stats_{LEAGUE_NAME}_{SEASON}.json'

if save_path.exists():
    with open(save_path, 'r', encoding='utf-8') as f:
        all_player_stats = json.load(f)
else:
    all_player_stats = {}
    #create an empty dictionary to eventually create a big JSON with all the matches in the league/season with player stats

for match_id in match_ids:
    if match_id in all_player_stats:
                continue
        #if a match was already extracted, skip it and move on

    url = f'https://api.pitchapi.dev/v1/matches/{match_id}/players'
    response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()
    #stop the request if we get an https error

    data = response.json()
    #convert that shi into a python dictionary

    all_player_stats[match_id] = data
    #append that new python dictionary into the new dict, match id as keys, all the data for said match as values
    save_path.parent.mkdir(parents=True, exist_ok=True)
    #save progress with each download/extraction

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(all_player_stats, f, indent=4)
        #make that dictionary into a json file for saving
    print(f'Got {match_id} extracted!')

print('Finished player stats extraction')

#print("Status:", response.status_code)
#print("Response:", response.text)
#print("URL:", response.url)

