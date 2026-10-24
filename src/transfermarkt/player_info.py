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

with sqlite3.connect(db_path) as connection:
    merged_transfermarkt = pd.read_sql_query(query, connection)
    #execute the written query, store it in a dataframe object