import sqlite3
from pathlib import Path
import pandas as pd

file_dir = Path(__file__).resolve().parents[2]

db_path = file_dir / 'database' / 'football.db'

query = """
SELECT tp.player_id, tp.name, tp.date_of_birth, tp.height_in_cm,
tv.market_value_in_eur, tv.date
FROM transfermarkt_players tp INNER JOIN transfermarkt_values tv 
ON tp.player_id = tv.player_id
"""
#merges the two tables together, has multiple rows for each player_id, based off their historical evaluations

with sqlite3.connect(db_path) as connection:
    merged_transfermarkt = pd.read_sql_query(query, connection)
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
FROM merged_transfermarkt
GROUP BY player_id
HAVING MAX(date)
"""