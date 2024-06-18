import argparse
import json
import openpyxl
import pandas as pd
import pickle
import xlsxwriter
from data_download import (
    daterange,
    download_data_for_tickers,
    fetch_and_save_exchange_rates,
    get_eur_exchange_rates,
    load_saved_data,
    load_saved_exchange_rates
)
from data_retrieval import (
    calculate_cash_position,
    calculate_daily_cash_position,
    calculate_daily_dividends,
    calculate_daily_portfolio_values,
    calculate_overall_performance,
    calculate_position_values_with_currency_adjustment,
    calculate_total_dividends,
    combine_cash_and_dividends,
    convert_to_gbp,
    load_exchange_rates,
    weekly_performance,
    combine_and_save_data
)
from utilities import load_dict_from_json

# Hardcoded API key for development purposes
api_key = "42c83d3d0b0e24c532ce1cd511d95724"

# Create the parser
parser = argparse.ArgumentParser(description='Generate weekly performance report for the portfolio.')
parser.add_argument('-download', action='store_true', help='Download new data instead of using saved data')
parser.add_argument('--weekly-report', action='store_true', help='Generate weekly performance report and save to Excel')
parser.add_argument('--transactions', default='../transactions.json', help='The path to the transactions JSON file')
parser.add_argument('--tickers', default='../current_tickers.json', help='The path to the current tickers JSON file')
parser.add_argument('--excel', action='store_true', help='Development stuffz')
#parser.add_argument('--update' action='store_true', help='updates the spreadsheets with data')

# Parse the arguments
args = parser.parse_args()

# (previous imports and argument parsing code)

if __name__ == "__main__":
    # Load Transactions and current tickers
    transaction_data = load_dict_from_json(args.transactions)
    current_tickers = load_dict_from_json(args.tickers)

    # Download or load the data based on the argument provided
    downloaded_fx = load_saved_exchange_rates()
    #downloaded_fx = get_eur_exchange_rates(api_key) if args.download else load_saved_exchange_rates()
    downloaded_data = download_data_for_tickers(transaction_data) if args.download else load_saved_data()

    if args.weekly_report:
        # Calculate position values with current exchange rates
        position_values_df = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data, downloaded_fx)

        total_portfolio_value = position_values_df[position_values_df['Company Name'] == 'Total Portfolio']['Position Value (GBP)'].iloc[-1]

        # Calculate weekly and overall performance
        weekly_perf_df = weekly_performance(transaction_data, downloaded_data, current_tickers)
        overall_perf_df = calculate_overall_performance(transaction_data, downloaded_data, current_tickers, total_portfolio_value)
        print(position_values_df.tail())

        # Merge weekly and overall performance DataFrames into the position_values_df based on 'Company Name'
        report_df = position_values_df.merge(weekly_perf_df, on='Company Name', how='left')
        report_df = report_df.merge(overall_perf_df, on='Company Name', how='left')


        # Rename columns as per your format if needed
        report_df.rename(columns={
            'Position Value (GBP)': 'Value (£)',
            'Weekly Performance': 'Weekly Performance (%)',
            'Performance': 'Performance (%)'
        }, inplace=True)

        # Calculate the cash position
        cash_position = calculate_cash_position(transaction_data, "./databases/exchange_rates.pkl", downloaded_data, downloaded_fx)

        # Calculate total div received
        tot_div = calculate_total_dividends(transaction_data, downloaded_data, downloaded_fx)[1]

        # Create a new DataFrame row for the cash position
        cash_row = pd.DataFrame([["Cash", cash_position, "---", tot_div]], columns=report_df.columns)

        # Append the cash position row to the report DataFrame
        report_df = pd.concat([report_df, cash_row], ignore_index=True)

        # Select and reorder the columns for the final report
        report_df = report_df[['Company Name', 'Weekly Performance (%)', 'Performance (%)', 'Value (£)']]

        # Save the DataFrame to an Excel file
        report_df.to_excel('weekly_report.xlsx', index=False)


        ## ===============================
        ## Prettifying the excel file here

        excel_file_path = 'weekly_report.xlsx'

        # Create a Pandas Excel writer using xlsxwriter as the engine
        writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
        report_df.to_excel(writer, index=False, sheet_name='Weekly_Update')

        # Access the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Weekly_Update']

        # Define the format: centered text
        centered_format = workbook.add_format({'align': 'center', 'num_format': '0.00'})

        # Apply the format to the columns
        # Assuming 'Weekly Performance (%)', 'Performance (%)', 'Value (£)' are in columns B, C, D
        for col in ['B', 'C', 'D']:
            worksheet.set_column(f'{col}:{col}', None, centered_format)

        # Close the Pandas Excel writer and output the Excel file
        writer.close()

        print("Weekly report generated and saved to 'weekly_report.xlsx'")


# Calculate daily cash position

daily_cash_position = calculate_daily_cash_position(transaction_data, downloaded_fx, downloaded_data)
print(daily_cash_position)

daily_dividends = calculate_daily_dividends(transaction_data, downloaded_data, downloaded_fx)
print(daily_dividends)

daily_portfolio_values = calculate_daily_portfolio_values(transaction_data, downloaded_data, downloaded_fx)

fin = combine_and_save_data(daily_portfolio_values, daily_cash_position, daily_dividends)
