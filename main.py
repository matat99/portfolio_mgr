# IMPORTANT IMPORTANT for future reference NTT DO COMO: selling it we made 422.27 profit and got 74.35 in dividends


import yfinance as yf
import pandas as pd
import json
from datetime import date,timedelta

# Load tickers from JSON file
with open('current_tickers.json', 'r') as file:
    tickers_dict = json.load(file)

# Load transactions from JSON file
with open('transactions.json', 'r') as file:
    transactions_dict = json.load(file)


# Create an empty portfolio dictionary 
portfolio_dict = {}

# Record Transactions

def get_price_on_date(ticker, date_str):
    """
    Get the closing price of a given stock ticker on a specific date.

    Parameters:
    ticker (str): The ticker symbol of the stock.
    date_str (str): The date to get the price for, in 'YYYY-MM-DD' format.

    Returns:
    float: The closing price on the specified date. 
           Returns 'No data' if no price data is available for the date.
    """
    # Convert date string to datetime
    check_date = pd.to_datetime(date_str)

    # Set a date range around the target date
    start_date = (check_date - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    end_date = (check_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d')

    try:
        # Fetch data for the date range
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # Extract data for the target date
        if check_date in data.index:
            return data.loc[check_date, 'Close']
        else:
            return 'No data'
    except Exception as e:
        return f'Error: {e}'


# Populate the portfolio dictionary
for ticker, transactions in transactions_dict.items():
    # Skip if there are no transactions for the ticker
    if not transactions:
        continue

    # Sort transactions by date
    transactions_sorted = sorted(transactions, key=lambda k: pd.to_datetime(k['date']))

    # Get the first transaction
    first_transaction = transactions_sorted[0]

    # Fetch the price on the date of the first transaction
    price = get_price_on_date(ticker, first_transaction['date'])

    # Add the ticker to the portfolio dictionary with the value, price, and date
    portfolio_dict[ticker] = {
        'value': first_transaction['amount'],
        'price': price,
        'date': first_transaction['date'],
    }

# Print the portfolio dictionary
for ticker, data in portfolio_dict.items():
    print(f"{ticker}: {data}")




