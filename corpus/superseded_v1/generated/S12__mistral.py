import pandas as pd
import numpy as np

# Assume you have a CSV file `large_table.csv` with the following structure:
# column1, column2, ..., columnN
data = pd.read_csv('large_table.csv')

# Set the desired sample size
sample_size = int(len(data) * 0.01)  # 1% sample

# Create a random index of the desired sample size
sample_index = np.random.choice(len(data), size=sample_size, replace=False)

# Select the rows for the sample
sample_data = data.iloc[sample_index]

# Calculate summary statistics
statistics = {
    'count': sample_data.shape[0],
    'mean': sample_data.mean(),
    'standard_deviation': sample_data.std(),
    'min': sample_data.min(),
    'max': sample_data.max(),
    'quantiles': {'Q1': sample_data.quantile(0.25), 'Q3': sample_data.quantile(0.75)}
}

# Print the results
print("Data Quality Report")
for key, value in statistics.items():
    print(f"{key}: {value}")
