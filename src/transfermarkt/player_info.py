import sqlite3
from pathlib import Path
import pandas as pd
import sys

file_dir = Path(__file__).resolve().parents[2]

db_path = file_dir / 'database' / 'football.db'

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON

query = """
SELECT tp.player_id, tp.name, tp.date_of_birth, tp.height_in_cm,
tv.market_value_in_eur, tv.date
FROM transfermarkt_players tp INNER JOIN transfermarkt_values tv 
ON tp.player_id = tv.player_id
"""
#merges the two tables together, has multiple rows for each player_id, based off their historical evaluations

with sqlite3.connect(db_path) as reading:
    merged_transfermarkt = pd.read_sql_query(query, reading)
    #execute the written query, store it in a dataframe object

with sqlite3.connect(db_path) as connection:
    merged_transfermarkt.to_sql(
        'merged_transfermarkt',
        connection,
        if_exists='replace',
        index=False)
#print(merged_transfermarkt.head())

grouping_query = """
SELECT * 
FROM 
    (SELECT *, ROW_NUMBER()
    OVER(PARTITION BY player_id
    ORDER BY date DESC) as rn
        FROM merged_transfermarkt
        WHERE date <= ?)
WHERE rn == 1
"""
season_cutoff = '2026-05-24'
with sqlite3.connect(db_path) as reading:
    grouped_merged_df = pd.read_sql_query(grouping_query, reading,
                                          params=(season_cutoff,))
    #execute the grouping query onto the merged transfermarkt dataset
    #41402 rows, 7 columns
grouped_merged_df = grouped_merged_df.rename(columns={'name' : 'player_name'})
print(grouped_merged_df.head())

league = LEAGUE_NAME.replace(' ', '_')

table_name = f'outfield_season_stats_{league}_{SEASON}'

pitchapi_query = f"""
SELECT player_id, player_name
FROM "{table_name}"
"""
with sqlite3.connect(db_path) as reading:
    pitchapi_names_df = pd.read_sql_query(pitchapi_query,reading)
    #read the query, execute it on the outfieldplayerstats table
    #return a dataframe that has all the player ids and player names from the pl25/26 season dataset

merged_df = pd.merge(grouped_merged_df, pitchapi_names_df, on='player_name', how='inner')