from sklearn.ensemble import IsolationForest
from sklearn.inspection import permutation_importance
import pandas as pd

# Load the data
df = pd.read_csv('sales_data.csv')

# Filter out the 'date' and 'sales' columns
X = df[['sales']]

# Create an Isolation Forest model
model = IsolationForest(n_estimators=100, contamination=0.03)

# Fit the model on the sales data
model.fit(X)

# Predict the labels for each observation
y_pred = model.predict(X)

# Create a binary column 'is_outlier' based on the prediction
df['is_outlier'] = y_pred

# Reset the index for easier analysis
df.reset_index(drop=True, inplace=True)

# Print the days with unusually high or low sales
print(df[df['is_outlier'] == 1])
