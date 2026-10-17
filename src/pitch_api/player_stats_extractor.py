import os
import json
import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv, find_dotenv

file_dir = Path(__file__).resolve().parents[2]
#establish file path
input_file_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / 'matches_l_3UiOcj_2025.json'

load_dotenv(file_dir / '.env')
api_key = os.getenv('api_key_pitch')
#load the api key from the env file

with open(input_file_path, 'r', encoding='utf-8') as f:
    match_data = json.load(f)
    #load the json file into a python dictionary

league_matches = match_data['data']['matches']
for match in league_matches:
    match_id = match['id']
print(match_id)


url = f'https://api.pitchapi.dev/v1/matches/{match_id}/players'

headers = {'X-API-KEY' : api_key}

response = requests.get(url, headers=headers, timeout=30)

#print("Status:", response.status_code)
#print("Response:", response.text)
#print("URL:", response.url)
response.raise_for_status()

data = response.json()
print(data.keys())
