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


query = f"""
SELECT *
FROM "{table_name}"
"""
#select everything from our dataset 

with sqlite3.connect(db_path) as connection:
    df = pd.read_sql_query(query, connection)
#establish our connection to the table

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
from sklearn.model_selection import cross_val_predict, KFold


x_train, x_test, y_train, y_test = train_test_split(x_features, y_features,
                                                    test_size = 0.2,
                                                    train_size = 0.8,
                                                    random_state = 42)

y_train_log = np.log(y_train)
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

log_predictions = cross_val_predict(
    model,
    x_train,
    y_train_log,
    cv=5)

#convert predictions back into euros
predictions_eur = np.exp(log_predictions)
print(f"CV MAE: €{mean_absolute_error(y_train, predictions_eur):,.2f}")
print(f"CV RMSE: €{root_mean_squared_error(y_train, predictions_eur):,.2f}")
print(f"CV R²: {r2_score(y_train, predictions_eur):.4f}")

#model.fit(x_train, y_train_log)
#train the model





