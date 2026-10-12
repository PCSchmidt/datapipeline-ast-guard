import polars as pl
from glob import glob
from datetime import datetime

# Define the folder containing the CSV files
csv_folder = "path/to/csv/files"

# Define the output Parquet file path
output_parquet = "path/to/output/revenue_per_region_per_day.parquet"

# Initialize an empty DataFrame to store the results
result_df = pl.DataFrame()

# Loop through all CSV files in the folder
for csv_file in glob(f"{csv_folder}/*.csv"):
    # Read the CSV file
    df = pl.read_csv(csv_file)
    
    # Extract the region and date from the file name
    file_name = csv_file.split("/")[-1]
    region = file_name.split("_")[0]
    date = datetime.strptime(file_name.split("_")[1], "%Y%m%d").date()
    
    # Compute revenue per region per day
    df = df.with_column(
        pl.col("revenue").sum().alias("total_revenue"),
        pl.lit(region).alias("region"),
        pl.lit(date).alias("date")
    )
    
    # Append the result to the result DataFrame
    result_df = result_df.vstack(df)

# Save the result as Parquet
result_df.write_parquet(output_parquet)
