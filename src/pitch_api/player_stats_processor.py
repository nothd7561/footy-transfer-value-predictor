from pathlib import Path
import pandas as pd
import json 
import sys

file_dir = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON


input_file_path = file_dir / 'data' / 'pitch_api_data' / 'raw_data' / f'player_stats_{LEAGUE_NAME}_{SEASON}.json'

with open(input_file_path, 'r', encoding='utf-8') as f:
    player_stats_data = json.load(f)
    #load the json file into a python dictionary

player_data = []
#create an empty list, so that we will have a list of dicts at the end

for match_id, match_data in player_stats_data.items():
    #go through the key, value. match_id is the key of the overall dict, with data as a the value being a list of dicts
    for player in match_data['data']:
        #loop through each dict in the list of dicts
        row = {'match_id': match_id,
                'player_id': player['player']['id'],
                'player_name': player['player']['name'],
                'team_id': player['team_id']}
        #base info, first couple of columns

        for stat_category in player['stats']:
            #since each stat dict has stat categories, loop through each cateogry
            for stat_name, stat_info in stat_category['stats'].items():
                stat_key = stat_info['key']
                #what category we're covering
                stat_value = stat_info['stat']['value']
                #the value assigned to that category, like number of goals, etc


                #skip statistics without a useful key
                if not stat_key:
                    continue

                row[stat_key] = stat_value

            #keep denomianators for percentage statistics
                if 'total' in stat_info['stat']:
                    row[f'{stat_key}_total'] = stat_info['stat']['total']
                    #we account for stats that are considered percentages/fractions

        player_data.append(row)

stats_df = pd.DataFrame(player_data)

stats_df.to_csv(file_dir / 'data' / 'pitch_api_data' / 'processed_data' / f'player_stats_{LEAGUE_NAME}_{SEASON}.csv')

print(stats_df.head())
print(stats_df.shape)
