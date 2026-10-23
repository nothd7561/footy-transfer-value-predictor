import sqlite3
from pathlib import Path
import pandas as pd

file_dir = Path(__file__).resolve().parents[2]

db_path = file_dir / 'database' / 'football.db'


