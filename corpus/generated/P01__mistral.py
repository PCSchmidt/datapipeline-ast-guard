import os
import pandas as pd

def read_csv_files(folder_path):
    region_sales_dfs = {}

    for entry in os.listdir(folder_path):
        if entry.endswith(".csv"):
            region, day = entry.split("_")
            region_sales_dfs[(region, day)] = pd.read_csv(os.path.join(folder_path, entry))

    return region_sales_dfs

def total_revenue_per_region_per_day(region_sales_dfs):
    total_revenue = {}

    for region, day, sales_df in region_sales_dfs.values():
        total_revenue[(region, day)] = sales_df["Revenue"].sum()

    return total_revenue

def write_parquet(data, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for region, day, revenue in data.items():
        output_file = os.path.join(output_folder, f"{region}_{day}.parquet")
        data[region, day].to_parquet(output_file)

if __name__ == "__main__":
    input_folder = "daily_sales_csv"
    output_folder = "daily_sales_parquet"

    region_sales_dfs = read_csv_files(input_folder)
    total_revenue = total_revenue_per_region_per_day(region_sales_dfs)
    write_parquet(total_revenue, output_folder)
