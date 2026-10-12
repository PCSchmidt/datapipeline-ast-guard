import pandas as pd
from scipy import stats

def detect_anomalies(df, column='Sales'):
    # Calculate mean and standard deviation
    mean = df[column].mean()
    std = df[column].std()

    # Set the threshold for anomalies
    threshold = mean + 3 * std

    # Detect anomalous days
    anomalies = df[(df[column] > threshold)]

    # Return the date and sales value of anomalies
    return anomalies[['date', column]]

# Assuming your data is in a CSV file named 'sales_data.csv'
sales_data = pd.read_csv('sales_data.csv')
anomalies = detect_anomalies(sales_data)

# Print the anomalous days and their sales values
print(anomalies)
