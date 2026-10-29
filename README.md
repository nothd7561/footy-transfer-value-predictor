
# Football Transfer Value Predictor

A machine learning project where I try to predict a football player's **Transfermarkt market value after a Premier League season**, using their performances during that season.

I wanted to build something that involved more than just downloading a clean dataset and fitting a model. Most of this project involved collecting match data, combining it with Transfermarkt valuations, figuring out why players weren't matching properly, and then experimenting with different regression models. 

I created this because I saw this as an idea on Instagram, and I needed something to test what I've learned so far. 

AI Usage Disclosure: I used AI as a supporting tool throughout parts of this project, mainly for creating visualizations (including the interactive scatterplot), setting up configuration files, troubleshooting Git issues, and debugging. The overall project structure, data pipeline, feature engineering, model experimentation, and interpretation of the results were driven by my own decisions and understanding.

PS: Most of this README was created by AI

**Status:** Version 1 of the data pipeline and model is complete. A frontend/demo is something I may add later.


### Project Up Front

| Dataset | Model | 2025–26 MAE | 2025–26 R² |
| --- | --- | --- | --- |
| 1,424 player-season records | Random Forest | €9.29M | 0.6102 |

### Explore the Project

**[Interactive Player Valuation Scatterplot](https://nothd7561.github.io/footy-transfer-value-predictor/)**

**[Understanding the Results — Non-Technical Guide](NON_TECHNICAL_GUIDE.md)**

If you're unfamiliar with machine learning, I'd recommend reading the non-technical guide first. It explains what the model predicts, what the results mean, and where the model struggles.

## Table of Contents

- [Project Goals](#project-goals)
- [Tech Stack](#tech-stack)
- [Data Sources](#data-sources)
  - [PitchAPI](#pitchapi)
  - [Transfermarkt](#transfermarkt)
- [Data Pipeline](#data-pipeline)
- [Multi-Season Dataset](#multi-season-dataset)
  - [The Player-Matching Problem](#the-player-matching-problem)
- [Model Features](#model-features)
- [Machine Learning Approach](#machine-learning-approach)
  - [Preprocessing](#preprocessing)
  - [Model Experiments](#model-experiments)
- [Results](#results)
  - [Initial Single-Season Experiment](#initial-single-season-experiment)
  - [Grouped Cross-Validation](#three-season-experiment-grouped-cross-validation)
  - [Chronological Evaluation](#three-season-experiment-202526-chronological-evaluation)
- [Error Analysis](#error-analysis)
  - [Interactive Visualization](#interactive-visualization)
  - [My Football Insights](#my-football-insights)
- [Limitations and Possible Next Steps](#limitations-and-possible-next-steps)
- [Setup and Running the Project](#setup-and-running-the-project)
- [Roadmap](#roadmap)
- [Project Status](#project-status)

## Project Goals

- Build a working pipeline from raw football data to a machine learning dataset.
- Use player statistics, age, and position to estimate post-season market values.
- Compare models and feature choices instead of relying on one training run.
- Understand where and why the model makes mistakes, not just report an accuracy metric.

This predicts **market valuations, not actual transfer fees**. For example, the 2025–26 inputs are performances from that season, and the labels are Transfermarkt valuations recorded after the season ended (through July 2026). The model does **not** forecast values at the end of 2026–27.

## Tech Stack

- **Python** — collecting, processing, and modeling data
- **pandas / NumPy** — cleaning and feature engineering
- **SQLite** — storing match and season-level data
- **requests / python-dotenv** — working with the API and environment variables
- **RapidFuzz** — suggesting possible player-name matches
- **scikit-learn** — preprocessing, training, cross-validation, and evaluation

[↑ Back to Top](#football-transfer-value-predictor)

## Data Sources

### PitchAPI

I used PitchAPI to retrieve Premier League matches and match-level player statistics such as minutes, goals, assists, ratings, passes, chances created, and defensive actions. These get aggregated into one row per outfield player per season.

### Transfermarkt

I used historical Transfermarkt player information and valuations to get player attributes, positions, and the target market values. The two sources don't necessarily use the same player names or IDs, so merging them was a significant part of the project.

For each season, I use the **first available valuation after the final league match**, up to July 31 of that year. This keeps the target aligned with the full-season statistics rather than accidentally using a valuation from before the season ended. Players without a valuation in that window are excluded from the labeled dataset.

[↑ Back to Top](#football-transfer-value-predictor)

## Data Pipeline

1. Retrieve the league and match IDs for the selected season.
2. Request each match's player statistics, saving responses so an interrupted extraction can resume.
3. Convert the raw JSON into a match-level CSV.
4. Aggregate match statistics into season-level records in SQLite.
5. Calculate per-90 statistics and passing accuracy.
6. Match PitchAPI players to Transfermarkt records and select the relevant post-season valuation.
7. Check for ambiguous player matches before saving the ML table.
8. Train and evaluate regression models.

The files and SQLite tables are season-specific, so I can run the pipeline for another year without intentionally overwriting the previous season's dataset.

[↑ Back to Top](#football-transfer-value-predictor)

## Multi-Season Dataset

I started with 2025–26, then collected and processed 2023–24 and 2024–25 using the same pipeline.

| Season | Outfield players | Players with usable valuations | Coverage |
| --- | ---: | ---: | ---: |
| 2023–24 | 530 | 482 | 90.9% |
| 2024–25 | 518 | 482 | 93.1% |
| 2025–26 | 497 | 460 | 92.6% |
| **Total** | **1,545** | **1,424** | **92.2%** |

That's **1,424 labeled player-season records** across three seasons, versus 460 records in the initial version. A player appearing in multiple seasons is kept as a separate observation for each year.

### The player-matching problem

This was one of the more frustrating parts of the project. PitchAPI and Transfermarkt often label the same player differently, and completely different players can have the same name. For example, names such as *Danilo*, *Antony*, and *Jorginho* initially produced multiple Transfermarkt matches.

The current process is:

- Normalize names (lowercase, remove accents) and merge on the normalized name.
- Use a dictionary called `verified_ids` for ambiguous names with manually checked PitchAPI-to-Transfermarkt IDs.
- Use `fuzzy_verified_ids` when the same player has different names across the two sources.
- Generate suggestions with RapidFuzz for players who still don't match.
- Check for duplicate PitchAPI IDs before writing the finished ML table, rather than letting ambiguous matches into training.

In practice, I printed the ambiguous matches, reviewed candidate players' birth dates and positions, used AI as an aid to narrow down possibilities, and then **manually added the confirmed mappings** to `verified_ids`. The AI suggestions weren't treated as an automatic or authoritative match.

This worked for three Premier League seasons, but it's **not an efficient or scalable solution**. If I expand the dataset, I'd want a more systematic way of reconciling player IDs, with a review queue for uncertain matches instead of hardcoding every new exception.

[↑ Back to Top](#football-transfer-value-predictor)

## Model Features

| Feature | Description |
| --- | --- |
| `age` | Player's age at the season cutoff |
| `height_in_cm` | Height |
| `sub_position` | Player's position (one-hot encoded) |
| `appearances` | League appearances |
| `total_minutes` | League minutes played |
| `total_goals_per90` | Goals per 90 minutes |
| `total_assists_per90` | Assists per 90 minutes |
| `avg_rating` | Average match rating |
| `total_chances_created_per90` | Chances created per 90 |
| `total_defensive_actions_per90` | Defensive actions per 90 |
| `total_interceptions_per90` | Interceptions per 90 |
| `total_tackles_per90` | Tackles per 90 |
| `pass_accuracy` | Share of successful pass attempts |

**Target:** `market_value_in_eur`

I ended up preferring per-90 statistics over raw totals in the early feature experiments. They help describe a player's production relative to their playing time, while `total_minutes` still provides context about how much they actually played. Goalkeepers are excluded from this version.

[↑ Back to Top](#football-transfer-value-predictor)

## Machine Learning Approach

### Preprocessing

- Mean imputation for missing numerical data.
- Most-frequent imputation for missing position data.
- One-hot encoding for `sub_position`, ignoring unknown categories.
- Preprocessing inside a scikit-learn `Pipeline`, so it is fitted separately within training folds.

### Model experiments

I initially compared Linear Regression with Random Forest, then tested different tree depths, minimum leaf sizes, total versus per-90 statistics, and player position. I also tested training on `np.log(market_value_in_eur)` instead of the original euro values.

After expanding the dataset, I compared Random Forest with Gradient Boosting. Random Forest performed better in our grouped cross-validation experiment with the configurations tested.

The Random Forest configuration used for the final comparisons is:

```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=9,
    min_samples_leaf=3,
    random_state=42
)
```

For the multi-season experiment, I trained on **2023–24 and 2024–25** and evaluated on **2025–26**. I used `GroupKFold` for cross-validation on the historical training data, grouping by Transfermarkt player ID so that the same player's records wouldn't be split across training and validation within a fold.

The chronological 2025–26 evaluation asks a different question: how well does a model trained on previous seasons predict post-season market values for players in the next season? Returning players can appear in both the historical training seasons and the later test season.

[↑ Back to Top](#football-transfer-value-predictor)

## Results

### Initial single-season experiment

The original 2025–26-only dataset contained 460 labeled players, split into 368 training and 92 test records.

| Metric | Original-target CV | Log-target CV |
| --- | ---: | ---: |
| MAE | €9.26M | **€8.68M** |
| RMSE | €13.62M | **€13.60M** |
| R² | 0.5758 | **0.5769** |

The initial non-log model's held-out 92-player test results were **€11.27M MAE**, **€19.76M RMSE**, and **0.5648 R²**. This was an earlier experiment with a different train/test setup, so it isn't a like-for-like comparison with the chronological results below.

### Three-season experiment: grouped cross-validation

These metrics use out-of-fold predictions on the 2023–24 and 2024–25 training records, evaluated back in euros.

| Metric | Random Forest (log target) | Random Forest (raw euros) | Gradient Boosting (log target) |
| --- | ---: | ---: | ---: |
| MAE | **€8.72M** | €9.28M | €8.91M |
| RMSE | **€13.91M** | €14.07M | €14.19M |
| R² | **0.6232** | 0.6142 | 0.6078 |

The log-target Random Forest performed best in this historical grouped CV comparison.

### Three-season experiment: 2025–26 chronological evaluation

| Metric | Random Forest (log target) | Random Forest (raw euros) |
| --- | ---: | ---: |
| MAE | €10.40M | **€9.29M** |
| RMSE | €16.22M | **€14.46M** |
| R² | 0.5093 | **0.6102** |

The raw-euro Random Forest performed better on the 2025–26 evaluation set, even though the log version had slightly better historical CV scores. That tradeoff was worth investigating rather than assuming the log transformation was automatically better.

**Evaluation caveat:** I looked at 2025–26 results repeatedly while developing the project, so these chronological results are **exploratory**, not a completely untouched, unbiased final test. The different historical and chronological evaluation sets also mean their scores shouldn't be treated as directly interchangeable.

[Back to Top](#football-transfer-value-predictor)

## Error Analysis

The biggest issue is the model's **underestimation of expensive players**. With the raw-euro Random Forest, I grouped the 2025–26 predictions by their actual market values:

| Actual market-value range | Players | Average absolute error | Average signed error |
| --- | ---: | ---: | ---: |
| Under €10M | 122 | €4.69M | +€4.32M |
| €10M–30M | 216 | €5.79M | -€1.34M |
| €30M–60M | 82 | €13.40M | -€11.17M |
| Over €60M | 40 | €33.81M | -€33.81M |

A positive signed error means the model overestimated the player; a negative error means it underestimated them. Every player in the over-€60M group was underestimated in this evaluation.

The log-target model did better for players under €10M, but the raw-euro model reduced the absolute errors for the higher-value groups. Neither solved the underestimation of elite players.

Some of the largest errors involved **Erling Haaland, Alexander Isak, Cole Palmer, Estêvão, Florian Wirtz, and Moisés Caicedo**. Their valuations make it clear that one season's Premier League statistics aren't the only thing the market is considering.

### Interactive Visualization

I created an interactive scatterplot to compare predicted
and actual market values for the 2025–26 Premier League season.

Hover over each player to see their name, position,
actual market value, predicted value, and prediction error.

[Explore the interactive graph](https://nothd7561.github.io/footy-transfer-value-predictor/)

### My football insights 

When I analyzed the results of my model, my first thought was just that my model wasn't accurate. But when looking a bit deeper, I realize that my knowledge of the football world and its current standings could help explain the reasoning behind the model's lack in accuracy.

Printing out the 10 highest valued players we predicted, we could see that among the names are Bukayo Saka, William Estevao, Florian Wirtz, etc. Any football fan that kept up with the Premier League 25/26 season and before knows the history of those players with injuries and transfers. 

Specifically, Florian Wirtz established his high price tag in the Bundesliga, another top 5 league before moving to the Premier League. Wirtz has been underwhelming in his time at Liverpool, with his stats not accurately reflecting those he put up at Bayer Leverkusen. For others like Saka and Estevao, those two players sustained heavy injuries that crucially affected their ability to make significant contributions. Meaning that their price tag remained where it is because their abilities had not diminished, they were just plagued by injuries and couldn't get enough time to make an impact.

In summary, there are so much external factors that we just can't really cover with pure data that can influence a player's performance and market evaluation. At least for this project, the movement between top 5 leagues is shooting a bit far. Hopefully, I will be skilled enough to accomplish such a task.

[Back to Top](#football-transfer-value-predictor)

## Limitations and Possible Next Steps

- **Missing football context:** We don't currently model remaining contract duration, club strength, reputation, injury history, or a player's performances outside the Premier League.
- **Single-season performance as input:** A player's valuation can reflect several years of established ability and potential, even when their current season's statistics are underwhelming.
- **Position differences:** Attackers, midfielders, and defenders aren't evaluated on identical criteria. One possible V2 experiment is to train separate models by position, although that means fewer training samples for each model.
- **Player matching:** The manual `verified_ids` process doesn't scale well beyond a small number of seasons in one league.
- **Expanding to the other top-five European leagues:** This was part of my original idea, but it's substantially more complicated than just changing the league setting. It would introduce many more ambiguous player names, different league contexts, and players moving **between the top-five leagues**, requiring stable identity tracking across leagues and seasons. Without a better matching system, scaling the pipeline that way would be inefficient and error-prone.
- **Future testing:** A genuinely new, later season would provide a cleaner evaluation of the final model than repeatedly using 2025–26.

I'm stopping model development for V1 here. These are useful directions for future work, but I don't want to keep adding complexity just to chase a slightly better score.

[↑ Back to Top](#football-transfer-value-predictor)

## Setup and Running the Project

As I mentioned before, this project also took in external data specifically for the transfermarkt data.
The database for transfermarkt can be downloaded at this link : https://github.com/dcaribou/transfermarkt-datasets

    -Keep in mind, this is a database, we only need two csvs from this folder. If you wish to use the other ones that is fine, but most csvs contained here go over the GitHub Large File limit of 100MB, so you need to account for that.

### 1. Directory structure

**For the scripts to work as written, recreate a directory structure similar to the one in this repository.** A lot of the paths are built relative to the script location using `Path(__file__).resolve().parents[...]`. If you prefer a different structure, that's completely fine, but you'll need to change the corresponding paths in the scripts.

The important parts are:

```text
project-root/
├── .env                     # create locally; do not commit
├── .gitignore
├── config.py
├── README.md
├── database/
│   └── football.db          # created/populated by the data pipeline
├── data/
│   └── pitch_api_data/
│       ├── raw_data/
│       │   ├── leagues.json
│       │   └── 2024/         # example season folder
│       └── processed_data/
│           └── 2024/
└── src/
    ├── pitch_api/
    │   └── player_stats_extractor.py
    ├── transfermarkt/
    │   └── player_info.py
    └── train_model.py
```

The tree highlights the paths used by the scripts; other collection and processing scripts in the repo also need to be run. The `raw_data` and `processed_data` folders contain season-specific files. The Transfermarkt source tables (`transfermarkt_players` and `transfermarkt_values`) must also be present in `football.db` before running `player_info.py`.

### 2. Install dependencies

From the project root, set up a Python environment and install the libraries used by the scripts:

```bash
pip install pandas numpy requests python-dotenv scikit-learn rapidfuzz
```

### 3. API key and `.gitignore`

Create a `.env` file **in the project root**, not inside `src/`. The PitchAPI extraction scripts look there for the key:

```dotenv
api_key_pitch=YOUR_API_KEY_HERE
```

**Do not upload your real API key to GitHub.** Add this to `.gitignore` at minimum:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

You can also ignore generated/raw data and local database files if you don't want to commit them. Just remember that someone cloning the repo will then need to generate or obtain those files themselves. If an API key was ever committed, adding `.env` to `.gitignore` afterward does not remove the secret from Git history; the key should be rotated.

### 4. Configure the season

Set `LEAGUE_NAME`, `SEASON`, `MATCH_SEASON`, and `COUNTRY_CODE` as needed in `config.py`. `SEASON` is the starting year (for example, `2024` means 2024–25). The API's season argument and the local season-folder naming need to be consistent with the scripts.

The valuation windows in `player_info.py` are configured for the three Premier League seasons used here. New seasons or leagues may require adding their correct final-match dates.

### 5. Run the pipeline in order

1. Collect/confirm the league IDs and match IDs for the selected season.
2. Run `src/pitch_api/player_stats_extractor.py` to fetch each match's player data.
3. Run the JSON-to-CSV processing script.
4. Run the match-to-season SQLite aggregation script.
5. Make sure the historical Transfermarkt player and valuation tables are loaded into SQLite.
6. Run `src/transfermarkt/player_info.py` and resolve any reported duplicate-name matches before proceeding.
7. Repeat for any additional seasons, then run `src/train_model.py`.

The current training script selects the 2023 and 2024 tables for training and uses 2025 for chronological evaluation. If you add or remove seasons, update its SQL query and split accordingly.

[↑ Back to Top](#football-transfer-value-predictor)

## Roadmap

- [x] Collect and aggregate Premier League match statistics
- [x] Match PitchAPI and Transfermarkt records
- [x] Build season-specific SQLite datasets for 2023–24, 2024–25, and 2025–26
- [x] Engineer per-90 features and encode positions
- [x] Compare Linear Regression, Random Forest, and Gradient Boosting
- [x] Test raw-euro and log-transformed market-value targets
- [x] Evaluate with grouped cross-validation and a chronological season split
- [x] Analyze prediction errors by market-value range
- [ ] Write up my detailed football-specific interpretation of the largest errors
- [ ] Save the trained model and build an interactive demo
- [ ] (Possible V2) Position-specific models, additional leagues, and better cross-league player ID matching

[↑ Back to Top](#football-transfer-value-predictor)

## Project Status

**V1 modeling is complete.** The next steps are documenting the findings, making the repository easy to follow, and possibly building a small frontend to show the predictions.
