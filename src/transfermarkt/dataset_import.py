import pandas as pd
import sqlite3
from pathlib import Path

file_dir = Path(__file__).resolve().parents[2]

download_path_players = file_dir / 'data' / 'transfermarkt' / 'transfermarkt-datasets' / 'players.csv' / 'players.csv'

download_path_values = file_dir / 'data' / 'transfermarkt' / 'transfermarkt-datasets' /'player_valuations.csv' / 'player_valuations.csv'

db_path = file_dir / 'database' / 'football.db'
#establish the path for the database which we want to import the tables into
folder = file_dir / 'data' / 'transfermarkt'

for item in folder.rglob('*.csv'):
    print(item)

players_df = pd.read_csv(download_path_players)
values_df = pd.read_csv(download_path_values)
#read the csv's we downloaded into dataframes

with sqlite3.connect(db_path) as connection:
    players_df.to_sql('transfermarkt_players', connection, if_exists='replace', index=False)
    values_df.to_sql('transfermarkt_values', connection, if_exists='replace', index=False)
#establish a connection to the database, turning the dataframes into tables

query= """
SELECT tp.player_id, tp.first_name, tp.last_name, tp.date_of_birth, tp.position, tv.date, tv.market_value_in_eur
FROM transfermarkt_players as tp INNER JOIN transfermarkt_values as tv 
ON tp.player_id = tv.player_id
"""
#write the query for choosing the features that we need, join the player info table with the market value table 
#using the player_id column, since that's the column both tables share (the key)

with sqlite3.connect(db_path) as connection1:
    player_info_df = pd.read_sql_query(query, connection1)
    #actually execute the query

print(player_info_df)