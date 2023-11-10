import argparse
import pandas as pd
from utilities import load_dict_from_json
import openpyxl
import json
import pickle
import xlsxwriter
from data_retrieval import (
    calculate_overall_performance,
    weekly_performance,
    calculate_position_values_with_currency_adjustment,
    create_excel_with_dataframe,
    create_combined_ticker_table
)
from data_download import (
    download_data_for_tickers,
    load_saved_data,
    download_weekly_exchange_rates,
    load_saved_exchange_rates
)

# Hardcoded API key for development purposes
api_key = "42c83d3d0b0e24c532ce1cd511d95724"

# Create the parser
parser = argparse.ArgumentParser(description='Generate weekly performance report for the portfolio.')
parser.add_argument('-download', action='store_true', help='Download new data instead of using saved data')
parser.add_argument('--weekly-report', action='store_true', help='Generate weekly performance report and save to Excel')
parser.add_argument('--transactions', default='../transactions.json', help='The path to the transactions JSON file')
parser.add_argument('--tickers', default='../current_tickers.json', help='The path to the current tickers JSON file')
parser.add_argument('--excel', action='store_true', help='Development stuffz')

# Parse the arguments
args = parser.parse_args()

# (previous imports and argument parsing code)

if __name__ == "__main__":
    # Load Transactions and current tickers
    transaction_data = load_dict_from_json(args.transactions)
    current_tickers = load_dict_from_json(args.tickers)

    # Download or load the data based on the argument provided
    downloaded_fx = download_weekly_exchange_rates(api_key) if args.download else load_saved_exchange_rates()
    downloaded_data = download_data_for_tickers(transaction_data) if args.download else load_saved_data()

    if args.weekly_report:
        # Calculate position values with current exchange rates
        position_values_df = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data, api_key)

        # Assuming position_values_df includes 'Total Portfolio' as one of the rows
        total_portfolio_value = position_values_df[position_values_df['Company Name'] == 'Total Portfolio']['Position Value (GBP)'].iloc[0]

        # Calculate weekly and overall performance
        weekly_perf_df = weekly_performance(transaction_data, downloaded_data, current_tickers)
        overall_perf_df = calculate_overall_performance(transaction_data, downloaded_data, current_tickers, total_portfolio_value)

        # Merge weekly and overall performance DataFrames into the position_values_df based on 'Company Name'
        report_df = position_values_df.merge(weekly_perf_df, on='Company Name', how='left')
        report_df = report_df.merge(overall_perf_df, on='Company Name', how='left')

        # Rename columns as per your format if needed
        report_df.rename(columns={
            'Position Value (GBP)': 'Value (£)',
            'Weekly Performance': 'Weekly Performance (%)',
            'Performance': 'Performance (%)'
        }, inplace=True)

        # Select and reorder the columns for the final report
        report_df = report_df[['Company Name', 'Weekly Performance (%)', 'Performance (%)', 'Value (£)']]

        # Save the DataFrame to an Excel file
        report_df.to_excel('weekly_report.xlsx', index=False)
        print("Weekly report generated and saved to 'weekly_report.xlsx'")

## dev

# Convert the sample dataframe to a string with a CSV format and write it to a text file
pkl_file_path = 'downloaded_data.pkl'

with open(pkl_file_path, 'rb') as file:
    downloaded_data_pkl = pickle.load(file)

# Check the type of the loaded data
print(f"Data type: {type(downloaded_data_pkl)}")

# If it's a dictionary, print its keys and some sample data
if isinstance(downloaded_data_pkl, dict):
    for key, value in downloaded_data_pkl.items():
        print(f"\nKey: {key}")
        # Assuming the value is a DataFrame or a similar structure, print the first few rows
        print(value.head())
else:
    # If it's not a dictionary, just print out the raw data
    print(downloaded_data_pkl)

# Debug the 'COLD' and '4I1.F' tickers specifically
if 'COLD' in downloaded_data:
    print("COLD data before processing:", downloaded_data['COLD'])
else:
    print("COLD data not found.")

if '4I7.F' in downloaded_data:
    print("4I7.F data before processing:", downloaded_data['4I7.F'])
else:
    print("4I7.F data not found.")


create_combined_ticker_table(downloaded_data)




