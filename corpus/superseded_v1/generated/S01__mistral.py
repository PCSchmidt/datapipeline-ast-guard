from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import os
import fastparquet as fp

class SalesSchema(BaseModel):
    date: str
    region: str
    sales: float

def read_sales_files(directory: str) -> List[SalesSchema]:
    sales_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(directory, filename), header=None)
            df.columns = ["date", "region", "sales"]
            sales_data = df.apply(SalesSchema.parse_raw, axis=1).tolist()
            sales_list.extend(sales_data)
    return sales_list

def compute_revenue(sales_data: List[SalesSchema]) -> Dict[str, Dict[str, float]]:
    revenue_by_region_and_date = {}
    for sale in sales_data:
        date, region, sales = sale.date, sale.region, sale.sales
        if date not in revenue_by_region_and_date:
            revenue_by_region_and_date[date] = {}
        if region not in revenue_by_region_and_date[date]:
            revenue_by_region_and_date[date][region] = 0.0
        revenue_by_region_and_date[date][region] += sales
    return revenue_by_region_and_date

def write_parquet(data: Dict[str, Dict[str, float]], output_path: str):
    for date, revenue_by_region in data.items():
        df = pd.DataFrame.from_dict(revenue_by_region, orient='index')
        df.columns = [date]
        fp.write_dataframe(df, os.path.join(output_path, date))

if __name__ == "__main__":
    landing_folder = "landing"
    output_path = "output"
    os.makedirs(output_path, exist_ok=True)

    sales_data = read_sales_files(landing_folder)
    revenue_by_region_and_date = compute_revenue(sales_data)
    write_parquet(revenue_by_region_and_date, output_path)
