import pandas as pd
from datetime import datetime

def fill_missing_data_to_csv(input_csv_file_path, output_csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv_file_path, usecols=['Date', 'Price'])

    # Convert date strings to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort the dates in ascending order, as we will fill forward
    df.sort_values('Date', inplace=True)

    # Create a new DataFrame that includes all dates from the earliest date in the data to the current date
    all_dates = pd.date_range(start=df['Date'].min(), end=datetime.today(), freq='D')

    # Create a new DataFrame with all dates and merge with the existing data
    df_full = pd.DataFrame({'Date': all_dates})
    df_full = df_full.merge(df, on='Date', how='left')

    # Use ffill() to fill NaN values with the previous day's Price
    df_full['Price'].ffill(inplace=True)

    # Write the resulting DataFrame to a new CSV file
    df_full.to_csv(output_csv_file_path, index=False)
    return f"Filled data written to {output_csv_file_path}"

# Example usage:
# The user would replace '/path/to/your/inputfile.csv' and '/path/to/your/outputfile.csv' with the actual file paths.
output_file = fill_missing_data_to_csv('./benchmark.csv', 'filled_benchmark.csv')
# print(output_file)
