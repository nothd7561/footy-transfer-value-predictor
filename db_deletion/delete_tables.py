import sqlite3
from pathlib import Path

file_dir = Path(__file__).resolve().parents[1]
db_path = file_dir / 'database' / 'football.db'

tables_to_delete = [
    'outfield_match_stats_Premier_League_2024',
    'outfield_season_stats_Premier_League_2024',
    'goalie_match_stats_Premier_League_2024',
    'player_ml_data_Premier_League_2024'
]

with sqlite3.connect(db_path) as connection:
    for table in tables_to_delete:
        connection.execute(f'DROP TABLE IF EXISTS "{table}"')
        print(f'Deleted: {table}')