import polars as pl

def read_data(file_path):
    return pl.read_csv(file_path)

def merge_data(orders, refunds):
    return orders.left_semi_join(refunds, on=['customer_id', 'order_date'], how='outer')

def calculate_clv(df):
    return (df.groupby('customer_id')
           .agg({'order_value': pl.sum(), 'refund_value': pl.sum()})
           .with_columns(pl.when(pl.col('refund_value').is_null(), pl.col('order_value'))
                          .otherwise(pl.col('order_value') - pl.col('refund_value')))
           .rename({'order_value': 'total_spent', 'refund_value': 'total_refunded'}))

def main():
    orders = read_data('orders.csv')
    refunds = read_data('refunds.csv')

    clv = calculate_clv(merge_data(orders, refunds))
    clv.write_csv('clv.csv')

if __name__ == "__main__":
    main()
