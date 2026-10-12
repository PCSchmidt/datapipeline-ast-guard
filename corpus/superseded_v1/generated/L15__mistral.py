import pandas as pd

def get_data_stats(file_name):
    # Read the file
    data = pd.read_csv(file_name)

    # Display the first 5 rows of the DataFrame
    print("First 5 rows of the data:")
    print(data.head())

    # Calculate basic statistics
    print("\nBasic Statistics:")
    print("Number of rows: ", data.shape[0])
    print("Number of columns: ", data.shape[1])
    print("Mean of all columns: ", data.mean())
    print("Standard Deviation of all columns: ", data.std())
    print("Minimum values of all columns: ", data.min())
    print("Maximum values of all columns: ", data.max())

# Call the function with the file name
get_data_stats("large_data.csv")
