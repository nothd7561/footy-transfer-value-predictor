import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import requests

load_dotenv()
#assumes .env file is in the same directory as this script

api_key = os.getenv('API_key')
#use api key without hardcoding it into the script

url = 'https://api.football-data.org/v4/competitions/'

headers = {
    'X-Auth-Token': api_key
}

params = {
    'season': 2025
}

response = requests.get(url, headers=headers) #params=params)

print(response.status_code)
if response.status_code == 200:
    data = response.json()
    print(data.keys())