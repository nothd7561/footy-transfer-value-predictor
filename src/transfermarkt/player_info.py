import sqlite3
from pathlib import Path
import pandas as pd

file_dir = Path(__file__).resolve().parents[2]

db_path = file_dir / 'database' / 'football.db'

query= """
SELECT tp.player_id,
     tp.first_name, 
     tp.last_name, 
     tp.date_of_birth,
     tp.position, 
     tv.date, 
     tv.market_value_in_eur
FROM transfermarkt_players as tp INNER JOIN transfermarkt_values as tv 
ON tp.player_id = tv.player_id
"""
#write the query for choosing the features that we need, join the player info table with the market value table 
#using the player_id column, since that's the column both tables share (the key)

with sqlite3.connect(db_path) as connection1:
    player_info_df = pd.read_sql_query(query, connection1)
    #actually execute the query on the database, and return the result as a dataFrame

with sqlite3.connect(db_path) as connection:
    player_info_df.to_sql(
        'player_overall_info',
        connection,
        if_exists='replace',
        index=False
    )
###CREATE A TABLE OF THE MERGED TABLES OF PLAYER CHARACTERISTICS AND PLAYER MARKET VALUES NAMED PLAYER OVERALL INFO

query_season = """
SELECT player_id, first_name, last_name, date_of_birth, position, date, market_value_in_eur
FROM (
    SELECT *, ROW_NUMBER() OVER (
            PARTITION BY player_id
            ORDER BY date DESC) AS rn
    FROM player_overall_info
    WHERE date <= '2026-05-24')
WHERE rn = 1
"""
#query to get player info for before the end of 25/26 season

with sqlite3.connect(db_path) as connection1:
    season_values_df = pd.read_sql_query(query_season, connection1)
    #actually execute the query
season_values_df['season'] = 2025
#set the season for 2025, bound to change later on

season_values_df['full_name'] = (
    season_values_df['first_name'].fillna('') + ' ' + season_values_df['last_name'].fillna('')).str.strip()
#combine the first and last names of the season df, so that we can match the names to search for players in pitchapi table
#if theres an NaN value, fill it.

with sqlite3.connect(db_path) as connection2:
    players_match = pd.read_sql_query(
        """
        SELECT player_id, player_name
        FROM outfield_season_stats
        """,
        connection2
    )
#apply the query to the outfield_season pitchapi table, store it in a df called player_match

players_match['clean_name'] = (
    players_match['player_name'].str.lower().str.strip())

season_values_df['clean_name'] = (
    season_values_df['full_name'].str.lower().str.strip())
#create a standardized name column for both df's , a non-case sensitive one, for merging

pitch_transfer = pd.merge(players_match, season_values_df, how='inner', on='clean_name')
#merge the pitchapi table with the adjusted transfermarkt table

missing_names = []
#print(pitch_transfer.head())

for name1 in players_match['player_name']:
    if name1 not in pitch_transfer['player_name'].values:
        missing_names.append(name1)
print(len(missing_names))

#print("PitchAPI players:", players_match['player_id'].nunique())

#print("Matched PitchAPI players:",pitch_transfer['player_id_x'].nunique())

#print("Transfermarkt players:",season_values_df['player_id'].nunique())
