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

features = [
    'age',
    'height_in_cm',
    'appearances',
    'total_minutes',
    'total_goals',
    'total_assists',
    'avg_rating',
    'total_chances_created',
    'total_defensive_actions',
    'total_interceptions',
    'total_tackles',
    'pass_accuracy']

x_features = df[features] #our x features

y_features = df['market_value_in_eur'] #our y feature(what we want to predict)

#print(x.isna().sum())
#look for missing values in features to consider imputation methods

from sklearn.model_selection import train_test_split, cross_validate
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

x_train, x_test, y_train, y_test = train_test_split(x_features, y_features,
                                                    test_size = 0.2,
                                                    train_size = 0.8,
                                                    random_state = 42)



numerical_processor = Pipeline([('imputing', SimpleImputer(strategy='mean'))])
#create a pipeline for imputing misisng values with mean imputation

depths = [3,5,7,9,11,13,15]
#so far, 9 returned the lowest rmse around 13.8mil
#the rmse hit a dip on 9 

leaf_sizes = [3,5,7,9,11,13,15]
#a leaf size of 3 produced our lowest rmse


model = Pipeline([('imputer', numerical_processor),
                       ('regressor', RandomForestRegressor(n_estimators=100,
                                                           max_depth=9,
                                                           min_samples_leaf=3,
                                                           random_state=42))])
#create the pipeline for the regression model, including the randomforest and imputation
#we already tuned our hyperparameters

cv_results = cross_validate(model, x_train, y_train, cv=5,
                            scoring={'mae': 'neg_mean_absolute_error',
                            'rmse': 'neg_root_mean_squared_error',
                            'r2': 'r2'})
#run the cross validation models for 5 folds 

model.fit(x_train, y_train)
#train our model on the data
print(f"CV RMSE: {-cv_results['test_rmse'].mean():,.2f}")
rf = model.named_steps['regressor']

importance_df = pd.DataFrame({
    'feature': features,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print(importance_df)


