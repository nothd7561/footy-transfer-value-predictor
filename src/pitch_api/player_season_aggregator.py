import pandas as pd
from pathlib import Path
import sys
import sqlite3

file_dir = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(file_dir))

from config import LEAGUE_NAME, SEASON

#Paths
input_file = (
    file_dir / 'data' / 'pitch_api_data' / 'processed_data'
    / f'player_stats_{LEAGUE_NAME}_{SEASON}.csv'
)

db_path = file_dir / 'database' / 'football.db'
db_path.parent.mkdir(parents=True, exist_ok=True)

#Generate table names based on league and season
league = LEAGUE_NAME.replace(' ', '_')

match_table = f'outfield_match_stats_{league}_{SEASON}'
season_table = f'outfield_season_stats_{league}_{SEASON}'
goalie_table = f'goalie_match_stats_{league}_{SEASON}'

df = pd.read_csv(input_file)

df['is_goalkeeper'] = df['saves'].notna()
#identify goalkeepers by usingthe saves column

df_played = df[df['minutes_played'] > 0].copy()
#keep only players with minutes played

#Separate outfield players and goalkeepers
df_outfield = df_played[df_played['is_goalkeeper'] == False].copy()
df_goalie = df_played[df_played['is_goalkeeper'] == True].copy()

with sqlite3.connect(db_path) as connection:
    df_outfield.to_sql(
        match_table,
        connection,
        if_exists='replace',
        index=False
    )

    df_goalie.to_sql(
        goalie_table,
        connection,
        if_exists='replace',
        index=False
    )
#save the dataframes to sql tables

query = f"""
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

FROM "{match_table}"
GROUP BY player_id
"""
#aggregate match values into season totals

with sqlite3.connect(db_path) as connection:
    outfield_player_db = pd.read_sql_query(query, connection)
    #execute the query aggregation

outfield_player_db['season'] = SEASON
outfield_player_db['league'] = LEAGUE_NAME


per90_features = [
    'total_goals',
    'total_assists',
    'total_chances_created',
    'total_defensive_actions',
    'total_interceptions',
    'total_clearances',
    'total_recoveries',
    'total_tackles'
]#stats we want on per 90 

for feature in per90_features:
    outfield_player_db[f'{feature}_per90'] = (
        outfield_player_db[feature]
        / outfield_player_db['total_minutes']
        * 90
    )#calculate per 90 features by looping through the list

outfield_player_db['pass_accuracy'] = (
    outfield_player_db['total_accurate_passes']
    / outfield_player_db['total_pass_attempts'].replace(0, float('nan'))
)#calculate the passing accuracy for the players


# Save the aggregated season-level data
with sqlite3.connect(db_path) as connection:
    outfield_player_db.to_sql(
        season_table,
        connection,
        if_exists='replace',
        index=False
    )

with sqlite3.connect(db_path) as connection:
    connection.execute("DROP TABLE IF EXISTS outfield_season_stats")
    connection.execute("DROP TABLE IF EXISTS outfield_player_stats")
    connection.execute("DROP TABLE IF EXISTS goalie_stats")
    #drop the former tables that didn't have specified naming conventions