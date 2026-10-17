import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import requests
import json
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
#locate the overall folder of the project

league = 'PL'  # Premier League
season = 2025  # the season I want data from, so since 2025 its season 25/26

file_path = project_dir / 'data' / 'raw_data' /f'football_data_{league}_{season}.json'
#assign the path/name to the file where the data will be stored

url = f'https://api.football-data.org/v4/competitions/{league}/teams'
#url with the league and season to get the data from

load_dotenv(project_dir / '.env')
api_key = os.getenv('API_key')
#load the API key from the .env file

headers = {
    'X-Auth-Token': api_key
}
params = {
    'season': season
}

if file_path.exists():
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    #if the file already exists, load the data from it instead of making a new API request
    print('File already exists. Loaded data from file.')

else:
    response = requests.get(url, headers=headers,params=params,timeout=30)
    #make an API request, with a 30-second timeout to avoid waiting indefinitely

    response.raise_for_status()
    #return the HTTPError if the request was unsuccessful
    
    data = response.json()
    #parse the json response into a Python dictionary
    print('File does not exist. Fetching data from API.')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        #save the data to a JSON file for future use

teams = data['teams']
print(len(teams))
