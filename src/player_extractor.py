import os
import pathlib as Path
import pandas as pd
import json

project_dir = Path(__file__).resolve().parent.parent
#locate the overall folder of the project

league = "PL"
season = 2025

file_path = project_dir / "data" / "raw" / f"teams_{league}_{season}.json"
#find the saved JSON file

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    #load said JSON file into a Python dictionary

teams = data['teams']

player_list = []

for team in teams:
    for player in team['squad']:
        player_data = {
            'team_id': team['id'],
            'team_name': team['name'],
            'player_id': player['id'],
            'player_name': player['name'],
            'position': player['position'],
            'date_of_birth': player['dateOfBirth'],
            'nationality': player['nationality']
        }
        player_list.append(player_data)
        #append the data to the listl, so we have a list of dictionaries, perfect form for DataFrame

player_data_df = pd.DataFrame(player_list)
#convert the list of dictionaries into a DataFrame, which is a more convenient format for data analysis

