# Football Transfer Value Predictor

A machine learning project that estimates football players' market values using season-level performance statistics, player characteristics, and positional data.

The project builds a data pipeline from **PitchAPI** match statistics and historical **Transfermarkt** market valuations, stores processed data in **SQLite**, and trains regression models with **scikit-learn**.

> **Status:** Initial Premier League model built and evaluated. Currently expanding the dataset to additional seasons.

## Project Goals

- Collect and process football match statistics across Premier League seasons.
- Match player performance records with historical market valuations.
- Engineer features such as goals, assists, and tackles per 90 minutes.
- Compare regression methods and evaluate prediction errors.
- Investigate whether additional seasons and contextual features improve generalization.

## Tech Stack

- **Python** — data collection and modeling
- **pandas / NumPy** — data processing and feature engineering
- **SQLite** — season-specific tables and querying
- **requests / python-dotenv** — API access and credentials
- **RapidFuzz** — support for player-name matching
- **scikit-learn** — preprocessing, regression, and evaluation

## Data Sources

### PitchAPI

Match-level player performance data, including minutes, goals, assists, ratings, passing statistics, chances created, and defensive actions. Match statistics are aggregated into player-season records.

### Transfermarkt

Player attributes and historical market valuations. Records are matched to PitchAPI players using normalized names and verified identifier mappings where needed.

For the initial 2025–26 dataset, target valuations were selected from a window after the season ended and through July 2026, rather than from the start of the season. Historical seasons must use their own corresponding valuation windows.

## Data Pipeline

1. Retrieve Premier League match IDs for the configured season.
2. Download per-match player statistics, caching responses so interrupted runs can resume.
3. Convert raw JSON into structured match-level CSV data.
4. Aggregate player match statistics into season-level records and save them in SQLite.
5. Join player records to Transfermarkt attributes and historical market values.
6. Engineer per-90 metrics and passing accuracy.
7. Train and evaluate regression models using scikit-learn pipelines.

Files and database tables use season-specific names so additional seasons can be added without replacing existing seasons.

## Multi-Season Dataset Expansion

After completing the initial model using the 2025–26 Premier League season, the dataset was expanded to include the 2023–24 and 2024–25 seasons.

The same data collection and processing pipeline was reused across all three seasons. Each season's match-level player statistics were collected through PitchAPI, aggregated into season-level observations, and matched with historical Transfermarkt market valuations.

### Dataset Summary

| Season | Outfield Players | Players with Valuations | Coverage |
|---|---:|---:|---:|
| 2023–24 | 530 | 482 | 90.9% |
| 2024–25 | 518 | 482 | 93.1% |
| 2025–26 | 497 | 460 | 92.6% |
| **Total** | **1,545** | **1,424** | **92.2%** |

The expanded dataset contains **1,424 labeled player-season observations**, compared with 460 in the original dataset.

Players can appear in multiple seasons, with each season representing a separate observation.

### Data Integration and Validation

Combining PitchAPI and Transfermarkt required resolving differences in player names and identifiers.

The matching process includes:

- Normalizing player names by converting them to lowercase and removing accents.
- Matching records across data sources using normalized names.
- Resolving ambiguous names using manually verified player IDs.
- Using RapidFuzz to generate candidate matches for unmatched players.
- Validating that each PitchAPI player appears only once per season.
- Excluding players without market valuations in the selected post-season window.

Each season uses its own valuation window based on the Premier League's final match date, aligning player performance statistics with subsequent market valuations.

### Data Quality Challenges

During the expansion, multiple Transfermarkt players were found to share identical or similar names. For example, players named Antony, Danilo, and Jorginho initially matched multiple Transfermarkt records.

These ambiguous matches were reviewed using player IDs, dates of birth, positions, and other available information.

Verified mappings were reused across seasons to improve the consistency of the matching process.

The pipeline was also updated to automatically identify unresolved duplicate matches, preventing ambiguous records from entering the final machine learning dataset.

### Next Steps

The expanded dataset will be used to investigate whether additional historical training data improves market-value predictions.

The next experiment will:

1. Combine the three season-level datasets.
2. Train the Random Forest model using the 2023–24 and 2024–25 seasons.
3. Evaluate the model using 2025–26 as a chronological holdout.
4. Compare performance against the initial single-season experiment.
5. Analyze prediction errors and document model limitations.

The goal is to evaluate how well historical player performance generalizes to a subsequent Premier League season.

## Model Features

| Feature | Description |
| --- | --- |
| `age` | Player age |
| `height_in_cm` | Player height |
| `position` | Player position (one-hot encoded) |
| `appearances` | League appearances |
| `total_minutes` | League minutes played |
| `total_goals_per90` | Goals per 90 minutes |
| `total_assists_per90` | Assists per 90 minutes |
| `avg_rating` | Average player rating |
| `total_chances_created_per90` | Chances created per 90 minutes |
| `total_defensive_actions_per90` | Defensive actions per 90 minutes |
| `total_interceptions_per90` | Interceptions per 90 minutes |
| `total_tackles_per90` | Tackles per 90 minutes |
| `pass_accuracy` | Share of successful pass attempts |

**Target:** `market_value_in_eur`

Per-90 features describe productivity relative to playing time, while total minutes preserve information about season participation.

## Machine Learning Approach

### Preprocessing

- Missing numerical values: mean imputation.
- Missing position values: most-frequent imputation.
- Position: one-hot encoding with unknown categories ignored.
- Preprocessing is part of the model pipeline and is fitted within each training fold.

### Model Selection

Initial experiments compared **Linear Regression** with **Random Forest Regression**. Random Forest performed better in five-fold cross-validation.

The selected Random Forest configuration is:

```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=9,
    min_samples_leaf=3,
    random_state=42
)
```

Feature experiments compared raw totals, per-90 statistics, both together, and per-90 statistics with position. The per-90-plus-position configuration achieved the lowest cross-validation RMSE among those configurations.

### Log-Transformed Target

The project also evaluates training on the natural logarithm of market value (`np.log(y_train)`). Predictions are converted back into euros with `np.exp(...)` before scoring.

## Initial Results

The first labeled dataset contained **460 outfield player records** from the **2025–26 Premier League season**. The initial split used **368 training** and **92 test** records.

### Five-Fold Cross-Validation (Training Partition)

Both configurations below were compared using out-of-fold predictions evaluated in euros.

| Metric | Original Random Forest | Log-Target Random Forest |
| --- | ---: | ---: |
| MAE | €9,261,688.82 | **€8,683,392.20** |
| RMSE | €13,616,701.54 | **€13,599,119.80** |
| R² | 0.5758 | **0.5769** |

The log-target model improved cross-validation MAE by approximately **6.2%**, while RMSE and R² changed only slightly.

### Held-Out Test Results (Original Target Only)

| Metric | Result |
| --- | ---: |
| MAE | €11,269,599.47 |
| RMSE | €19,756,560.59 |
| R² | 0.5648 |

**Important:** These held-out test results are for the original (non-log-target) model. The log-target model has not been independently evaluated on a new untouched test set. Its reported improvements are cross-validation results, not claims about new-season performance.

## Limitations

- **Small dataset:** The initial experiment covers one league season, with only 368 training records.
- **Limited context:** Club strength, contract duration, reputation, and other market factors are not modeled yet.
- **High-value outliers:** Large errors on expensive players can disproportionately influence RMSE.
- **Record matching:** Names and identifiers from different sources require validation.
- **Time consistency:** Player inputs and target valuations must be aligned to the correct season and prediction date.
- **Generalization:** A future-season evaluation is still needed to assess performance across time.

## Setup

Install the principal dependencies:

```bash
pip install pandas numpy requests python-dotenv scikit-learn rapidfuzz
```

Create a `.env` file in the repository root with your own API credentials. **Do not commit API keys.** Configure the target league and season in `config.py`.

Run the collection and processing scripts in pipeline order: matches → match-player statistics → structured CSV → season aggregation → valuation matching. The modeling script is `src/train_model.py`.

> Exact script commands will be documented after the multi-season data pipeline is finalized.

## Roadmap

- [x] Retrieve Premier League player statistics
- [x] Integrate historical Transfermarkt valuations
- [x] Store and aggregate records with SQLite
- [x] Engineer per-90 features
- [x] Train and compare regression models
- [x] Tune Random Forest hyperparameters
- [x] Add position encoding
- [x] Compare raw and log-transformed targets using cross-validation
- [x] Evaluate the initial model on a held-out test set
- [ ] Complete the 2024–25 Premier League dataset
- [ ] Add more historical seasons
- [ ] Evaluate with a chronological train/test split
- [ ] Investigate club and contract context
- [ ] Analyze high-error predictions and create visualizations
- [ ] Build a player-value prediction interface

## Project Status

The initial end-to-end pipeline and model are working. The current focus is **expanding historical data coverage** and testing whether the model can generalize to other seasons.
