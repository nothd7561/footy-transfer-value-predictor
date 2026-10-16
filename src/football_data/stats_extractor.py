import os
import requests
from pathlib import Path
from dotenv import load_dotenv

project_dir = Path(__file__).resolve().parent.parent

load_dotenv(project_dir / '.env')
api_key = os.getenv('API_key')

player_id = 98816

url = f"https://api.football-data.org/v4/persons/{player_id}/matches"

headers = {
    'X-Auth-Token': api_key
}
params = {
    "competitions": "PL",
    "dateFrom": "2025-08-01",
    "dateTo": "2026-07-01",
    "limit": 100
}

response = requests.get(url, headers=headers, params=params, timeout=30)

if response.status_code == 200:
    data = response.json()
    print(data)