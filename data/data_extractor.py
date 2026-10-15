import os
from pathlib import Path
from dotenv import load_dotenv

# Find the folder containing data_extractor.py
script_folder = Path(__file__).resolve().parent

# Go up to the project folder
env_path = script_folder.parent / ".env"

# Check the file location
print("Looking for:", env_path)
print("File exists:", env_path.is_file())

# Load the .env file
loaded = load_dotenv(dotenv_path=env_path, override=True)

print("Dotenv loaded:", loaded)

# Retrieve the variable using YOUR exact spelling
api_key = os.getenv("API_key")

print("API key found:", bool(api_key))

from pathlib import Path

print("Script location:", Path(__file__).resolve())
print("Parent folder:", Path(__file__).resolve().parent)
print("Project folder:", Path(__file__).resolve().parent.parent)

print("Files in project folder:")
for file in Path(__file__).resolve().parent.parent.iterdir():
    print(repr(file.name))