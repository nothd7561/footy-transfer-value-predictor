import pandas as pd
from pathlib import Path
import sys
import sqlite3

file_dir = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON

input_file = file_dir / 'data' / 'pitch_api_data' / 'processed_data' / f'player_stats_{LEAGUE_NAME}_{SEASON}.csv'

#df_played = df[(df['minutes_played'].notna())  & (df['minutes_played'] > 0)].copy()
#create a copy of the original df, this one only with players that actually had some amount of gametime

db_path = file_dir / 'database' / 'football.db'
db_path.parent.mkdir(parents=True, exist_ok=True)
#creates directory for me in case the directory wasn't already created

df = pd.read_csv(input_file)
#read the csv and store it into the df variable

with sqlite3.connect(db_path) as connection:
    #open up the path to the databse
    df.to_sql(
        'player_match_stats',
        connection, #the connection between the python and the sqlite database
        if_exists='replace',
        index=False
    )
    #takes our dataframe and stores it into a sql table
    #if the table already exists, replace it

query = """
SELECT
    player_id,
    MAX(player_name) AS player_name,
    COUNT(*) AS appearances,
    SUM(minutes_played) AS total_minutes,
    SUM(goals) AS total_goals,
    SUM(assists) AS total_assists,
    AVG(rating_title) AS avg_rating
FROM player_match_stats
WHERE minutes_played > 0
GROUP BY player_id
"""
#the query for the sqlite database

with sqlite3.connect(db_path) as connection1:
    player_season_df = pd.read_sql_query(query, connection1)

player_season_df['goals_per90'] = (player_season_df['total_goals']/ player_season_df['total_minutes']
    * 90
)#calculate the number of goals per 90 minutes played