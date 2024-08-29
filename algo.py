
import pandas as pd
import numpy as np
import itertools


# Load the spreadsheet
file_path = 'vegasodds.xlsx'
df = pd.read_excel(file_path, index_col=0)

# Function to convert spread to win probability
def spread_to_probability(spread):
    return 1 / (1 + np.exp(spread / 2.2))

# Convert the spreads to probabilities
for week in df.columns:
    df[week] = df[week].apply(spread_to_probability)


# List of teams you would like to exclude (e.g., Teams you've already picked)
excluded_indices = ['Cowboys']
# Filter out the excluded indices
df = df.drop(excluded_indices)


# Generate all combinations of picking 1 record from each "Week" column
week_columns = df.filter(like="Week")
combinations = list(itertools.product(*[week_columns[col] for col in week_columns.columns]))
# Convert the combinations into a DataFrame
combinations_df = pd.DataFrame(combinations, columns=week_columns.columns)

# Create an associated dataframe that has the team names associated with each win probability
# Create a mapping of value to index for each column
value_to_index = {}
for col in df.columns:
    value_to_index[col] = {value: idx for idx, value in df[col].items()}

# Replace the values in combinations_df with their associated index values
index_combinations_df = combinations_df.apply(
    lambda row: pd.Series({col: value_to_index[col][row[col]] for col in row.index}),
    axis=1
)

# Remove rows from combinations_df and index_combinations_df where the same team was selected more than once
combinations_df = combinations_df.loc[
    ~(index_combinations_df.nunique(axis=1) < index_combinations_df.shape[1])
]

index_combinations_df = index_combinations_df.loc[
    ~(index_combinations_df.nunique(axis=1) < index_combinations_df.shape[1])
]



## Get the combination that gives the highest average win probability
# Calculate the average value for each row
combinations_df['average'] = combinations_df.mean(axis=1)
# Find the row with the highest average value
row_with_max_average = combinations_df.loc[combinations_df['average'].idxmax()]


## Get the combination that gives the highest number of weeks with a probability above 90%
# Count the number of values above 90% only in columns with "Week" in the name
week_columns = combinations_df.filter(like="Week")
combinations_df['count_above_90'] = (week_columns > 0.9).sum(axis=1)
# Find the row with the highest count of values above 90%
row_with_most_above_90 = combinations_df.loc[combinations_df['count_above_90'].idxmax()]

