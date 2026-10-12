import pandas as pd
import numpy as np

def cltv_calculation(data):
    # Calculate the total spend, total refunds, and net spend for each customer
    grouped_data = data.groupby('customer_id')
    total_spend = grouped_data['order_value'].sum()
    total_refunds = grouped_data['refund_value'].sum()
    net_spend = total_spend - total_refunds

    # Calculate the number of orders, refunds, and active days for each customer
    orders = len(grouped_data.filter(like='order_date').sum(axis=0))
    refunds = len(grouped_data.filter(like='refund_date').sum(axis=0))
    active_days = (grouped_data['order_date'].max() - grouped_data['order_date'].min()).dt.days

    # Calculate the average order value, purchase frequency, and customer lifetime for each customer
    avg_order_value = net_spend / orders
    purchase_frequency = orders / active_days
    customer_lifetime = net_spend / refunds

    # Create a new DataFrame with the CLTV metrics
    cltv_df = pd.DataFrame({
        'customer_id': data['customer_id'],
        'total_spend': total_spend,
        'total_refunds': total_refunds,
        'net_spend': net_spend,
        'orders': orders,
        'refunds': refunds,
        'active_days': active_days,
        'avg_order_value': avg_order_value,
        'purchase_frequency': purchase_frequency,
        'customer_lifetime': customer_lifetime
    })

    return cltv_df

# Load the dataset and calculate the CLTV for each customer
data = pd.read_csv('orders_and_refunds.csv')
cltv_df = cltv_calculation(data)

# Save the CLTV DataFrame as a CSV file
cltv_df.to_csv('customer_lifetime_value.csv', index=False)
