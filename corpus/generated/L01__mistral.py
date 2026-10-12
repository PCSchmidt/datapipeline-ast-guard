import polars as pl
import os
import pandas as pd

def read_csv_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    df_list = [pd.read_csv(os.path.join(directory, f)) for f in files]
    return df_list

def combine_and_group(df_list):
    df = pl.concat(df_list).to_dataframe()
    df = df.merge(pd.DataFrame({"date": df["date"].dt.date, "day": df["date"].dt.day_of_year}), on="date", how="left")
    df = df.merge(pd.DataFrame({"region": ["region_" + str(i) for i in range(1, len(df) + 1)}), on="region", how="left")
    df = df.merge(pd.DataFrame({"revenue": df["revenue"]}), on="region", how="left")
    df = df.drop(["region", "region_x"], axis=1)
    df = df.groupby(["day", "region"]).sum().reset_index()
    return df

def save_parquet(df, directory):
    for region, group in df.groupby("region"):
        group.to_parquet(os.path.join(directory, f"{group['region'].iloc[0]}_revenue_per_day.parquet"))

def main():
    input_folder = "path/to/your/csv/files"
    output_folder = "path/to/output/parquet/files"

    df_list = read_csv_files(input_folder)
    df = combine_and_group(df_list)
    save_parquet(df, output_folder)

if __name__ == "__main__":
    main()
