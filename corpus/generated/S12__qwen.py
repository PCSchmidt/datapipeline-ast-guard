import pandas as pd
import numpy as np

# Load the large dataset (assuming it's a CSV file)
# Replace 'large_dataset.csv' with the path to your large dataset file
large_dataset = pd.read_csv('large_dataset.csv')

# Define the sample size
sample_size = 1000  # Adjust this value based on your needs

# Randomly sample a subset of the data
sampled_data = large_dataset.sample(n=sample_size, random_state=42)

# Print summary statistics
print(sampled_data.describe(include='all'))
