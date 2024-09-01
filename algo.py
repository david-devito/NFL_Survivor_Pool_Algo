
import pandas as pd
import numpy as np
import itertools
import random


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
excluded_indices = []
# Filter out the excluded indices
df = df.drop(excluded_indices)


# Simulated Annealing Parameters
initial_temperature = 2000
cooling_rate = 0.99
iterations = 20000
topNSolutionNum = 1000

# Function to calculate the objective (average probability)
def calculate_average_probability(teams):
    valid_probs = []
    for team, week in zip(teams, df.columns):
        if team in df.index and not pd.isna(df.loc[team, week]):
            valid_probs.append(df.loc[team, week])
    return np.mean(valid_probs) if valid_probs else 0

# Function to get a random neighbor by swapping teams between two random weeks
def get_random_neighbor(current_solution):
    #print("Current Solution:", current_solution)
    
    # Find indices of weeks with teams assigned
    assigned_indices = [i for i, team in enumerate(current_solution) if team is not None]
    if not assigned_indices:
        return current_solution  # No change if no teams are assigned
    
    # Select a random index to replace
    index_to_replace = random.choice(assigned_indices)
    
    # Find available teams not currently in the solution
    available_teams = {team for team in df.index if team not in current_solution}
    if not available_teams:
        return current_solution  # No change if no available teams
    
    # Get the current team at the selected index
    current_team = current_solution[index_to_replace]
    
    # If the current team is the only team left, no need to replace
    if len(available_teams) == 1 and current_team in available_teams:
        return current_solution
    
    # Remove the current team from available teams
    available_teams.discard(current_team)
    
    # Select a new team from available teams
    new_team = random.choice(list(available_teams))
    
    # Create a new solution by replacing the selected team
    new_solution = current_solution[:]
    new_solution[index_to_replace] = new_team
    
    #print("New Solution:", new_solution)
    
    return new_solution

# Initialize a random valid solution
def initialize_solution():
    solution = []
    available_teams = set(df.index)
    for week in df.columns:
        possible_teams = available_teams - set(solution)
        if possible_teams:
            team = random.choice(list(possible_teams))
            solution.append(team)
        else:
            solution.append(None)
    return solution

current_solution = initialize_solution()
current_score = calculate_average_probability(current_solution)

# Initialize the best solution found so far
best_solution = current_solution[:]
best_score = current_score

topNSolutions = pd.DataFrame(columns=list(df.columns) + ['Score'])

# Simulated Annealing Loop
temperature = initial_temperature
for i in range(iterations):
    # Get a neighbor solution
    neighbor_solution = get_random_neighbor(current_solution)
    neighbor_score = calculate_average_probability(neighbor_solution)
    
    # Calculate the acceptance probability
    if temperature > 0:
        acceptance_probability = np.exp((neighbor_score - current_score) / temperature)
    else:
        acceptance_probability = 0

    # Decide whether to accept the neighbor solution
    if neighbor_score > current_score or random.random() < acceptance_probability:
        current_solution = neighbor_solution
        current_score = neighbor_score
    
    # Update the best solution found so far
    if current_score > best_score:
        best_solution = current_solution
        best_score = current_score
    
    # Print the iteration number every 2000 iterations
    if (i + 1) % 2000 == 0:
        print(f"Iteration {i + 1}: Current best score = {best_score}, Temperature = {temperature:.2f}")
    
    # Cool down the temperature
    temperature *= cooling_rate


    # Store top N Solutions
    new_row_df = pd.DataFrame([neighbor_solution])
    new_row_df['Score'] = round(neighbor_score,3)
    new_row_df.columns=topNSolutions.columns
    
    topNSolutions = pd.concat([topNSolutions, new_row_df], ignore_index=True)
    topNSolutions = topNSolutions.sort_values(by='Score', ascending=False)
    topNSolutions = topNSolutions.head(topNSolutionNum).reset_index(drop=True)



# Final Output
# Filter out teams with NaN probabilities
valid_teams = [team for team in best_solution if team in df.index]
best_probs = [df.loc[team, week] if not pd.isna(df.loc[team, week]) else np.nan
              for team, week in zip(valid_teams, df.columns)]

# Ensure the DataFrame creation matches the number of columns
result_df = pd.DataFrame([best_probs], columns=df.columns[:len(best_probs)])
result_df['average'] = result_df.mean(axis=1)

print("Best combination of teams:", best_solution)
print("Best probabilities:", best_probs)
print("Highest average probability:", best_score)


topNSolutions.to_csv('TopNSolutions.csv')









