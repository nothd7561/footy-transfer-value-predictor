import sqlite3
import pandas as pd
from pathlib import Path
import sys
import joblib

file_dir = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(file_dir))

from config import LEAGUE_NAME, SEASON

db_path = file_dir / 'database' / 'football.db'

league = LEAGUE_NAME.replace(' ', '_')
table_name = f'player_ml_data_{league}_{SEASON}'


query = """
SELECT * FROM player_ml_data_Premier_League_2023

UNION ALL

SELECT * FROM player_ml_data_Premier_League_2024

UNION ALL

SELECT * FROM player_ml_data_Premier_League_2025
"""
#select everything from our dataset 

with sqlite3.connect(db_path) as connection:
    df = pd.read_sql_query(query, connection)
#establish our connection to the table

#print(df.groupby('season').size())
#print('Total observations:', len(df))

column_names = df.columns.to_list()
#print(column_names)

numerical_features = [
    'age',
    'height_in_cm',
    'appearances',
    'total_minutes',
    'total_goals_per90',
    'total_assists_per90',
    'avg_rating',
    'total_chances_created_per90',
    'total_defensive_actions_per90',
    'total_interceptions_per90',
    'total_tackles_per90',
    'pass_accuracy'
]
categorical_features = ['sub_position']
features = numerical_features + categorical_features #our x features

x_features = df[features]

y_features = df['market_value_in_eur'] #our y feature(what we want to predict)

#print(x.isna().sum())
#look for missing values in features to consider imputation methods

from sklearn.model_selection import train_test_split, cross_validate
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np
from sklearn.model_selection import cross_val_predict, GroupKFold


train_df = df[df['season'].isin([2023, 2024])]
test_df = df[df['season'] == 2025]
#

x_train = train_df[features]
y_train = train_df['market_value_in_eur']

x_test = test_df[features]
y_test = test_df['market_value_in_eur']

groups = train_df['player_id_tm']


#y_train_log = np.log(y_train)
#log transform our y training values (the euro prices)

numerical_processor = Pipeline([('imputing', SimpleImputer(strategy='mean'))])
#create a pipeline for imputing misisng values with mean imputation

categorical_processor = Pipeline([('imputing', SimpleImputer(strategy='most_frequent')),
                                  ('encoding', OneHotEncoder(handle_unknown='ignore'))])

depths = [3,5,7,9,11,13,15]
#so far, 9 returned the lowest rmse around 13.8mil
#the rmse hit a dip on 9 

leaf_sizes = [3,5,7,9,11,13,15]
#a leaf size of 3 produced our lowest rmse

preprocessor = ColumnTransformer([
    ('numeric', numerical_processor, numerical_features),
    ('category', categorical_processor, categorical_features)
])

model = Pipeline([('preprocessor', preprocessor),
                       ('regressor', RandomForestRegressor(n_estimators=100,
                                                           max_depth=9,
                                                           min_samples_leaf=3,
                                                           random_state=42))])
#create the pipeline for the regression model, including the randomforest and imputation
#we already tuned our hyperparameters

eur_predictions = cross_val_predict(
    model,
    x_train,
    y_train,
    cv=GroupKFold(n_splits=5),
    groups=groups)

#convert predictions back into euros


print(f"cv mae : €{mean_absolute_error(y_train, eur_predictions):,.2f}")
print(f"cv rmse : €{root_mean_squared_error(y_train, eur_predictions):,.2f}")
print(f"cv r^2 : {r2_score(y_train, eur_predictions):.4f}")

model.fit(x_train, y_train)

#train the model
model_dir = file_dir / 'models'
model_dir.mkdir(parents=True, exist_ok=True)
#create a directory to store trained models

model_path = model_dir / 'random_forest_2025.joblib'

joblib.dump(model, model_path)
#save our trained random forest model

print(f'Model saved to: {model_path}')

#predict market values for the 2025/26 season
test_predictions_eur = model.predict(x_test)

#convert predictions back into euros


print("test results")
print(f"test mae : €{mean_absolute_error(y_test, test_predictions_eur):,.2f}")
print(f"test rmse : €{root_mean_squared_error(y_test, test_predictions_eur):,.2f}")
print(f"test r^2 : {r2_score(y_test, test_predictions_eur):.4f}")


error_df = test_df[['player_name_pitch', 'age', 'sub_position', 'market_value_in_eur']].copy()
#store the actual and predicted market values for each test player

error_df['predicted_value'] = test_predictions_eur
#create a column of the predicted values

error_df['error'] = (error_df['predicted_value'] - error_df['market_value_in_eur'])
#calculate how far each prediction is from the actual value

error_df['absolute_error'] = error_df['error'].abs()
#absolute error for the error value

print(
    error_df.sort_values(
        'absolute_error',
        ascending=False
    ).head(10).to_string(
        index=False,
        float_format=lambda x: f'{x:,.2f}'
    )
)

error_df['value_group'] = pd.cut(
    error_df['market_value_in_eur'],
    bins=[0, 10000000, 30000000, 60000000, float('inf')],
    labels=['Under €10M', '€10M–30M', '€30M–60M', 'Over €60M']
)

print(
    error_df.groupby('value_group', observed=True).agg(
        players=('absolute_error', 'count'),
        avg_absolute_error=('absolute_error', 'mean'),
        avg_error=('error', 'mean')
    )
)

output_dir = file_dir / 'data' / 'model_results'
output_dir.mkdir(parents=True, exist_ok=True)

error_df.to_csv(output_dir / 'predictions_2025.csv', index=False)
#save predictions so we can create graphs separately
