import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt

file_dir = Path(__file__).resolve().parents[1]
#establish directiory for our file

results_path = file_dir / 'data' / 'model_results' / 'predictions_2025.csv'
#establish the path where our csv will come in from

df = pd.read_csv(results_path)

output_dir = file_dir / 'visualizations'
output_dir.mkdir(parents=True, exist_ok=True)

#graph 1 is actual vs predicted values

plt.figure(figsize=(9, 6))

sns.scatterplot(
    data=df,
    x='market_value_in_eur',
    y='predicted_value',
    alpha=0.6
)

max_value = max(df['market_value_in_eur'].max(), df['predicted_value'].max())

plt.plot(
    [0, max_value],
    [0, max_value],
    linestyle='--',
    color='red',
    label='Perfect prediction'
)

plt.xlabel('Actual Market Value (€)')
plt.ylabel('Predicted Market Value (€)')
plt.title('Actual vs Predicted Market Values (2025–26)')
plt.legend()
plt.tight_layout()

plt.savefig(output_dir / 'actual_vs_predicted.png', dpi=300)
plt.show()


#graph 2: average error by market value
df['value_group'] = pd.cut(
    df['market_value_in_eur'],
    bins=[0, 10000000, 30000000, 60000000, float('inf')],
    labels=['Under €10M', '€10M–30M', '€30M–60M', 'Over €60M']
)

grouped_errors = df.groupby(
    'value_group', observed=True
)['error'].mean().reset_index()

grouped_errors['error_millions'] = grouped_errors['error'] / 1000000

plt.figure(figsize=(9, 6))

sns.barplot(
    data=grouped_errors,
    x='value_group',
    y='error_millions'
)

plt.axhline(0, linestyle='--', color='black')

plt.xlabel('Market Value Group')
plt.ylabel('Average Prediction Error (€M)')
plt.title('Average Prediction Error by Market Value')
plt.tight_layout()

plt.savefig(output_dir / 'errors_by_value.png', dpi=300)
plt.show()


import plotly.express as px

#interactive scatterplot
#highlight the 10 players with the highest actual market values

df['top_10'] = 'Other Players'

top_10_indices = df.nlargest(
    10, 'market_value_in_eur'
).index

df.loc[top_10_indices, 'top_10'] = 'Top 10 Most Valuable'


#convert euro values to millions for easier reading
df['actual_millions'] = df['market_value_in_eur'] / 1000000
df['predicted_millions'] = df['predicted_value'] / 1000000
df['error_millions'] = df['error'] / 1000000


fig = px.scatter(
    df,
    x='actual_millions',
    y='predicted_millions',
    color='top_10',
    hover_name='player_name_pitch',
    hover_data={
        'sub_position': True,
        'age': True,
        'actual_millions': ':.2f',
        'predicted_millions': ':.2f',
        'error_millions': ':+.2f',
        'top_10': False
    },
    color_discrete_map={
        'Other Players': 'lightgray',
        'Top 10 Most Valuable': 'royalblue'
    },
    labels={
        'actual_millions': 'Actual Market Value (€M)',
        'predicted_millions': 'Predicted Market Value (€M)',
        'error_millions': 'Prediction Error (€M)',
        'sub_position': 'Position',
        'age': 'Age'
    },
    title='Actual vs Predicted Market Values (2025–26)'
)

max_value = max(
    df['actual_millions'].max(),
    df['predicted_millions'].max()
)

fig.add_shape(
    type='line',
    x0=0,
    y0=0,
    x1=max_value,
    y1=max_value,
    line=dict(color='red', dash='dash')
)

fig.update_traces(marker=dict(size=9, opacity=0.75))

fig.update_layout(
    template='plotly_white',
    legend_title_text='Player Group'
)

fig.write_html(
    output_dir / 'interactive_scatter.html',
    include_plotlyjs=True
)

fig.show()
