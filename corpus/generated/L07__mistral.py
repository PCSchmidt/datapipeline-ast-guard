import polars as pl
import pandas as pd
from datetime import timedelta

def assign_session_id(df):
    df = df.with_column(
        pl.col('user_id')
        .cumsum()
        .over(pl.Window.order_by('timestamp').every(timedelta(minutes=30)))
        .alias('session_id')
    )

    return df

clickstream = pd.read_csv("clickstream.csv")
polars_df = pl.DataFrame(clickstream)

result = assign_session_id(polars_df)
result.write_csv("output.csv")
