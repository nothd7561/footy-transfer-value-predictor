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