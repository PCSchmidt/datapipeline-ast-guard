import pandas as pd
from scipy.stats import scoreatpercentile

def detect_anomalies(data, q=0.01):
    q1 = data.quantile(q/2)
    q3 = data.quantile(1 - q/2)
    interquartile_range = q3 - q1

    iqr_lower_bound = q1 - (q * interquartile_range)
    iqr_upper_bound = q3 + (q * interquartile_range)

    anomalies = data[(data < iqr_lower_bound) | (data > iqr_upper_bound)]
    return anomalies

def main():
    df = pd.read_csv('sales_data.csv', parse_dates=['date'])
    sales_data = df['sales']
    threshold = 0.01  # Set the desired percentile for anomaly detection
    anomalies = detect_anomalies(sales_data, threshold)

    if not anomalies.empty:
        print(f"Anomalous sales detected on the following dates:")
        print(anomalies)

if __name__ == "__main__":
    main()
