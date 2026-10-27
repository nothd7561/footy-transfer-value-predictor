import sqlite3
from pathlib import Path
import pandas as pd
import sys
import unicodedata
from rapidfuzz import process, fuzz

def clean_name(name):
    if pd.isna(name):
        return ''

    name = str(name).lower().strip()

    name = unicodedata.normalize('NFKD', name)

    name = ''.join(
        char for char in name
        if not unicodedata.combining(char)
    )

    return name
#function to process names with accents into names without accents, so that we can match easier

file_dir = Path(__file__).resolve().parents[2]

db_path = file_dir / 'database' / 'football.db'

sys.path.insert(0, str(file_dir))
#our file dir points to the entire folder, to find the config file we have to convert the Path to a string
#config is in the root, this script is two files deeper

from config import LEAGUE_NAME, SEASON

season_end_dates = {
    2023: '2024-05-19',
    2024: '2025-05-25',
    2025: '2026-05-24'
}
#the final match date of each premier league season

season_end = season_end_dates[SEASON]
season_cutoff = season_end
valuation_deadline = f'{SEASON + 1}-07-31'
#use the correct valuation window based on our selected season

query = """
SELECT tp.player_id, tp.name, tp.date_of_birth, tp.height_in_cm,
tv.market_value_in_eur, tv.date, tp.sub_position
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
#returns one row per player, with their latest market value


with sqlite3.connect(db_path) as reading:
    grouped_merged_df = pd.read_sql_query(grouping_query, reading,
                                          params=(season_cutoff,))
    #execute the grouping query onto the merged transfermarkt dataset
grouped_merged_df = grouped_merged_df.rename(columns={'name' : 'player_name'})

league = LEAGUE_NAME.replace(' ', '_')

table_name = f'outfield_season_stats_{league}_{SEASON}'

pitchapi_query = f"""
SELECT *
FROM "{table_name}"
"""

with sqlite3.connect(db_path) as reading:
    pitchapi_names_df = pd.read_sql_query(pitchapi_query,reading)
    #read the query, execute it on the outfieldplayerstats table
    #return a dataframe with player ids and names from the selected season

pitchapi_names_df['clean_name'] = (
    pitchapi_names_df['player_name'].apply(clean_name))
#apply the name conversion function to all the names in the pitchapi and transfermarkt dataset

grouped_merged_df['clean_name'] = (
    grouped_merged_df['player_name'].apply(clean_name))

merged_df = pd.merge(
    pitchapi_names_df,
    grouped_merged_df,
    on='clean_name',
    how='left',
    suffixes=('_pitch', '_tm'))

verified_ids = {
    'p_07pCQk': 996897,    # Diego Gómez
    'p_0C0UVV': 472423,    # Reece James
    'p_0QA08f': 123682,    # Callum Wilson
    'p_0Qmeai': 357565,    # Rodri
    'p_0bJ5Go': 319859,    # Mathias Jensen
    'p_0fZWyR': 204103,    # Adama Traoré
    'p_12r3tb': 517894,    # Matheus Cunha
    'p_179WVr': 735570,    # João Gomes
    'p_1IqhK0': 466805,    # Nico González
    'p_1qdPAY': 192765,    # Ben Davies
    'p_2GOYVS': 800176,    # André
    'p_2VIcoo': 61841,     # Adam Smith
    'p_2dN9Ma': 432164,    # Igor Jesus
    'p_2nzhKi': 1193867,   # Pedro Lima
    'p_2siSV9': 435338,    # Gabriel
    'p_2xAAfF': 1086258,   # Souza
    'p_3QFLEl': 595809,    # Beto
    'p_3jvO7d': 817665,    # Pablo
    'p_48SKOM': 626724,    # João Pedro
    'p_1ivJgM': 206040,    # Raúl Jiménez
    'p_4apwGi': 345911,    # Ladislav Krejčí
    #2023/24 premier league duplicate name matches
    'p_1m6yay': 646658,    # Aaron Ramsey
    'p_074Ebr': 533086,    # Amadou Diallo
    'p_2nvpAR': 221025,    # André Gomes
    'p_1IIuQu': 602105,    # Antony
    'p_3xZuOY': 808509,    # Danilo
    'p_1OgyF5': 181778,    # Emerson
    'p_2B63Xc': 156501,    # Felipe
    'p_2whyrf': 537598,    # Fábio Vieira
    'p_49OZVg': 102017,    # Jorginho
    'p_3cmo8f': 480692,    # Luis Díaz
    'p_1eAcpC': 314210,    # Tom Davies
    'p_1SSVHn': 468249,    # Vitinho
    'p_3bDMsO': 52769,    # Willian
    'p_2wgk1K': 193098,    # Álex Moreno
        #2024/25 premier league duplicate name matches
    'p_1uwaOo': 695454,    # Chiquinho
    'p_02Tj1F': 447995,    # Ross Stewart
}
#the dictionary with all of the players that got repeated during the merge, because they share a name

correct_matches = merged_df[
    (~merged_df['player_id_pitch'].isin(verified_ids))| (merged_df['player_id_tm'] == merged_df['player_id_pitch'].map(verified_ids))].copy()

fuzzy_verified_ids = {
    'p_0i4lOF': 134270,    # Daniel Burn -> Dan Burn
    'p_12ZKIz': 340329,    # Joseph Willock -> Joe Willock
    'p_207PS8': 256178,    # Joseph Gomez -> Joe Gomez
    'p_0GpXw1': 503686,    # Daniel Ballard -> Dan Ballard
    'p_0gYBeC': 522784,    # Valentin Castellanos -> Taty Castellanos
    'p_0pVLLS': 585959,    # Arnaud Kalimuendo-Muinga
    'p_1E46UG': 1111589,   # Malick Diouf -> El Hadji Malick Diouf
    'p_1KYRdF': 240692,    # Reinildo -> Reinildo Mandava
    'p_2RKBhY': 568693,    # Pape Sarr -> Pape Matar Sarr
    'p_2cdntb': 525247,    # Max Kilman -> Maximilian Kilman
    'p_2d3a77': 606718,    # Toti Gomes -> Toti
    'p_2xRMQc': 503981,    # Valentino Livramento -> Tino Livramento
    'p_2xoong': 568157,    # Yeremi Pino -> Yeremy Pino
    'p_36IsBr': 748319,    # Charly Alcaraz -> Carlos Alcaraz
    'p_38JpnL': 406634,    # Matthew O'Riley -> Matt O'Riley
    'p_3ar7gC': 340321,    # Joshua Dasilva -> Josh Dasilva
    'p_3r80MJ': 430310,    # Andy Irving -> Andrew Irving
    'p_3ubYGy': 340324,    # Edward Nketiah -> Eddie Nketiah
    'p_4IvWuX': 607224,    # Hannibal Mejbri -> Hannibal
    'p_4U79m4': 184573,    # Victor Nilsson Lindelof -> Victor Lindelof
    'p_4dgH0u': 717411,    # Yehor Yarmoliuk -> Yegor Yarmolyuk
}
#list of fuzzy matched names

for pitch_id, tm_id in fuzzy_verified_ids.items():

    player_index = correct_matches[correct_matches['player_id_pitch'] == pitch_id].index
    #find the corresponding PitchAPI player

    if len(player_index) == 0:
        continue

    if len(player_index) > 1:
        print(f"there were multiple rows found for {pitch_id}")
        continue
    #this block of code accounts for players that we found were missing in one season, but present in another

    #find the corresponding Transfermarkt player
    tm_player = grouped_merged_df[
        grouped_merged_df['player_id'] == tm_id
    ]

    if tm_player.empty:
        print(f"No Transfermarkt player found for {pitch_id} (TM ID {tm_id})")
        continue

    #copy Transfermarkt information into the existing row
    for column in [
        'player_id',
        'date_of_birth',
        'height_in_cm',
        'sub_position',
        'market_value_in_eur',
        'date'
    ]:
        target_column = 'player_id_tm' if column == 'player_id' else column

        correct_matches.loc[player_index, target_column] = (
            tm_player.iloc[0][column]
        )

#find the first market valuation recorded after the season ended
post_season_query = """
SELECT player_id, market_value_in_eur, date
FROM (
    SELECT player_id, market_value_in_eur, date,
    ROW_NUMBER() OVER (
        PARTITION BY player_id
        ORDER BY date ASC
    ) AS rn
    FROM transfermarkt_values
    WHERE date > ? AND date <= ?
)
WHERE rn = 1
"""


with sqlite3.connect(db_path) as connection:
    post_season_values = pd.read_sql_query(
        post_season_query,
        connection,
        params=(season_end, valuation_deadline)
    )

#remove the old valuations, since they were recorded before the season ended
correct_matches = correct_matches.drop(
    columns=['market_value_in_eur', 'date']
)

#match the post-season valuations using the transfermarkt player ids
correct_matches = pd.merge(
    correct_matches,
    post_season_values,
    left_on='player_id_tm',
    right_on='player_id',
    how='left',
    validate='many_to_one'
)

correct_matches = correct_matches.drop(columns=['player_id'])

#check for players matched to multiple Transfermarkt records
#only print details if we still have ambiguous matches to resolve
duplicates = correct_matches[
    correct_matches.duplicated(subset=['player_id_pitch'], keep=False)
]

if not duplicates.empty:
    print("Unresolved duplicate player matches:")
    print(
        duplicates[
            [
                'player_id_pitch',
                'player_name_pitch',
                'player_id_tm',
                'date_of_birth',
                'sub_position',
                'height_in_cm'
            ]
        ].sort_values('player_name_pitch').to_string(index=False)
    )
    raise ValueError("Resolve duplicate player matches before saving the ML table")

#check how many players have a post-season market valuation
print(f"Season: {SEASON}/{SEASON + 1}")
print("Total players:", len(correct_matches))
print("Post-season valuations:", correct_matches['market_value_in_eur'].notna().sum())
print("Missing valuations:", correct_matches['market_value_in_eur'].isna().sum())

#find the players that still have missing market values after applying the known matches
missing_players = correct_matches[
    correct_matches['market_value_in_eur'].isna()
]

#use rapidfuzz to find possible matches for the remaining players
tm_names = grouped_merged_df['clean_name'].dropna().unique().tolist()

fuzzy_suggestions = []

for _, player in missing_players.iterrows():
    name = player['clean_name']
    pitch_id = player['player_id_pitch']
    pitch_name = player['player_name_pitch']

    matches = process.extract(
        name,
        tm_names,
        scorer=fuzz.ratio,
        limit=5
    )

    for match_name, score, index in matches:

        #find the transfermarkt ids that correspond to the suggested name
        candidates = grouped_merged_df[
            grouped_merged_df['clean_name'] == match_name
        ]

        for _, candidate in candidates.iterrows():
            fuzzy_suggestions.append({
                'pitch_id': pitch_id,
                'pitch_name': pitch_name,
                'tm_id': candidate['player_id'],
                'tm_name': candidate['player_name'],
                'similarity': score
            })

fuzzy_suggestions_df = pd.DataFrame(
    fuzzy_suggestions,
    columns=['pitch_id', 'pitch_name', 'tm_id', 'tm_name', 'similarity']
)
#create a dataframe to store our fuzzy name suggestions with both player ids, so that we can review them for future seasons

birth = pd.to_datetime(correct_matches['date_of_birth'])
#convert the date of birth to date time format
cutoff = pd.Timestamp(season_cutoff)
#make a timestamp for the season cutoff

correct_matches['age'] = ((cutoff - birth).dt.days / 365.25).floordiv(1).astype('Int64')
#make calculations for finding age

correct_matches['date'] = pd.to_datetime(correct_matches['date'])


correct_matches['valuation_age_days'] = (
    correct_matches['date'] - cutoff
).dt.days

final_table = f'player_ml_data_{league}_{SEASON}'
#name for the final table filled with the data

ml_data = correct_matches.dropna(
    subset=['market_value_in_eur']
).copy() #drops players without a market value in our post-season range
#makes a copy so that the original dataframe isn't affected

with sqlite3.connect(db_path) as connection:
    ml_data.to_sql(
        final_table,
        connection,
        if_exists='replace',
        index=False)


print(f"saved player records to {final_table}")
