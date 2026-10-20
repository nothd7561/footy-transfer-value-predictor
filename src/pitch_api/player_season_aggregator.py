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
df['is_goalkeeper'] = df['saves'].notna()
#pick out players with a non n/a saves

df_played = df[df['minutes_played'] > 0].copy()
#filter out only the players that have gotten game_time

df_outfield = df_played[df_played['is_goalkeeper'] == False].copy()
#return all the players that have is_goalkeeper as false; those are the actual field players
#make a copy so that when we create new features, we don't need to worry about the status of the original

df_goalie = df_played[df_played['is_goalkeeper'] == True].copy()
#return all players that have is_gk as true


with sqlite3.connect(db_path) as connection:
    #open up the path to the databse
    df_outfield.to_sql(
        'outfield_season_stats',
        connection, #the connection between the python and the sqlite database
        if_exists='replace',
        index=False
    )
    #takes our dataframe and stores it into a sql table
    #if the table already exists, replace it

    df_goalie.to_sql(
        'goalie_stats',
        connection,
        if_exists='replace',
        index=False
    )
query = """
SELECT
    player_id,
    MAX(player_name) AS player_name,
    COUNT(*) AS appearances,
    SUM(minutes_played) AS total_minutes,
    SUM(goals) AS total_goals,
    SUM(assists) AS total_assists,
    AVG(rating_title) AS avg_rating,

    SUM(touches) AS total_touches,
    SUM(accurate_passes) AS total_accurate_passes,
    SUM(accurate_passes_total) AS total_pass_attempts,

    SUM(chances_created) AS total_chances_created,
    SUM(defensive_actions) AS total_defensive_actions,
    SUM(interceptions) AS total_interceptions,
    SUM(clearances) AS total_clearances,
    SUM(recoveries) AS total_recoveries,
    SUM("matchstats.headers.tackles") AS total_tackles

FROM outfield_season_stats
GROUP BY player_id
"""
#the query for the sqlite database, implement the aggregation methods

with sqlite3.connect(db_path) as connection1:
    outfield_player_db = pd.read_sql_query(query, connection1)
    #actually execute the query

outfield_player_db['season'] = SEASON

outfield_player_db['goals_per90'] = (outfield_player_db['total_goals']/ outfield_player_db['total_minutes']
    * 90)

per90_features = [
    'total_goals',
    'total_assists',
    'total_chances_created',
    'total_defensive_actions',
    'total_interceptions',
    'total_clearances',
    'total_recoveries',
    'total_tackles'
]#make a list of all the stats that we want per 90 measure in

for feature in per90_features:
    outfield_player_db[f'{feature}_per90'] = (
        outfield_player_db[feature]
        / outfield_player_db['total_minutes']
        * 90
    )
#loop over every per 90 feature, create a column for each per 90 calculation
outfield_player_db['pass_accuracy'] = (outfield_player_db['total_accurate_passes'] / outfield_player_db['total_pass_attempts'])

with sqlite3.connect(db_path) as connection:
    outfield_player_db.to_sql(
        'outfield_player_stats',
        connection,
        if_exists='replace',
        index=False
    )


#print(outfield_player_db.shape)
#print(outfield_player_db.isna().sum().sort_values(ascending=False))
#print(outfield_player_db.duplicated(['player_id', 'season']).sum())