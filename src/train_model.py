import sqlite3
import pandas as pd
from pathlib import Path
import sys

file_dir = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(file_dir))

from config import LEAGUE_NAME, SEASON

db_path = file_dir / 'database' / 'football.db'

league = LEAGUE_NAME.replace(' ', '_')
table_name = f'player_ml_data_{league}_{SEASON}'


query = f"""
SELECT *
FROM "{table_name}"
"""
#select everything from our dataset 

with sqlite3.connect(db_path) as connection:
    df = pd.read_sql_query(query, connection)
#establish our connection to the table

column_names = df.columns.to_list()
print(column_names)

features = [
    'age',
    'height_in_cm',
    'appearances',
    'total_minutes',
    'total_goals',
    'total_assists',
    'avg_rating',
    'total_chances_created',
    'total_defensive_actions',
    'total_interceptions',
    'total_tackles',
    'pass_accuracy']

x = df[features] #our x features

y = df['market_value_in_eur'] #our y feature(what we want to predict)