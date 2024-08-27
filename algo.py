
import pandas as pd
import numpy as np




# Load the spreadsheet
file_path = 'vegasodds.xlsx'  # Correct the file path if needed
spreadsheet = pd.read_excel(file_path, index_col=0)

# Function to convert spread to win probability
def spread_to_probability(spread):
    return 1 / (1 + np.exp(spread / 2.2))

# Convert the spreads to probabilities
for week in spreadsheet.columns:
    spreadsheet[week] = spreadsheet[week].apply(spread_to_probability)

# Initialize list to keep track of picks - so that team's that are picked in an earlier week won't be chosen again
picked_teams = []

# Example restriction dictionary
restrictions = {'Bengals': ['Week1', 'Week3']}

def recommend_pick(schedule, picked_teams, restrictions):
    weeks = schedule.columns
    teams = schedule.index

    # Dynamic programming table to store the max probability
    dp = pd.DataFrame(index=teams, columns=weeks, data=0.0)
    
    # Fill in the probabilities for the first week
    for team in teams:
        if team not in restrictions or weeks[0] not in restrictions[team]:
            dp.at[team, weeks[0]] = schedule.at[team, weeks[0]]
        else:
            dp.at[team, weeks[0]] = -np.inf  # Set to negative infinity to avoid picking this team in the restricted week
    
    # Fill the DP table
    for i in range(1, len(weeks)):
        for team in teams:
            if team not in picked_teams:
                max_prob = -np.inf
                for prev_team in teams:
                    if prev_team not in picked_teams and dp.loc[prev_team, weeks[i-1]] != -np.inf:
                        prob = dp.loc[prev_team, weeks[i-1]] + schedule.loc[team, weeks[i]]
                        if prob > max_prob:
                            max_prob = prob
                if team not in restrictions or weeks[i] not in restrictions[team]:
                    dp.loc[team, weeks[i]] = max_prob
                else:
                    dp.loc[team, weeks[i]] = -np.inf  # Set to negative infinity to avoid picking this team in the restricted week
    
    # Backtrack to find the picks
    picks = []
    for week in weeks:
        best_team = dp[week].idxmax()
        while dp.at[best_team, week] == -np.inf:
            dp.drop(index=best_team, inplace=True)
            best_team = dp[week].idxmax()
        picks.append(best_team)
        picked_teams.append(best_team)
        dp.drop(index=best_team, inplace=True)
    
    return picks




# Get the recommended picks
picks = recommend_pick(spreadsheet, picked_teams, restrictions)

# Print the recommended picks
for week, pick in zip(spreadsheet.columns, picks):
    print(f"{week} pick: {pick}")

print("Picks:", picks)


