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
        position_values_df, total_portfolio_value = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data, api_key)

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




