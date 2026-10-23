import pandas as pd
import sqlite3
from pathlib import Path

###this is universal, it contains player info for multiple leagues

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

###imported the csvs for player characteristics and player values, converted them into a dataframe, then converted those dataframes into sql databases/tables