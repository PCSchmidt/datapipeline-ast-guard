import pandas as pd
from datetime import datetime

# Filter the data for the last quarter (assuming a fiscal year from Jan to Dec)
quarter_start = datetime(year=df['Date'].dt.year.iloc[0], month=10, day=1)
quarter_end = datetime(year=df['Date'].dt.year.iloc[0], month=12, day=31)
q4_data = df[(df['Date'] >= quarter_start) & (df['Date'] <= quarter_end)]

# Calculate total values for the quarter
q4_total_revenue = q4_data['Revenue'].sum()
q4_total_expenses = q4_data['Expenses'].sum()
q4_total_profit = q4_data['Profit'].sum()

# Create a new DataFrame with the summary information
quarterly_report = pd.DataFrame([
    {'Quarter': 'Q4', 'Revenue': q4_total_revenue, 'Expenses': q4_total_expenses, 'Profit': q4_total_profit}
])

# Save the quarterly report as a CSV file
quarterly_report.to_csv('quarterly_report.csv', index=False)
