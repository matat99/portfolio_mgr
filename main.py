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
# for ticker, data in portfolio_dict.items():
#     print(f"{ticker}: {data}")



import pandas as pd
from pandas.tseries.offsets import BDay
import yfinance as yf

def get_weekly_performance(tickers_dict):
    # Create a dictionary to store the performance for each ticker
    performance_dict = {}

    # Iterate through each ticker
    for name, ticker in tickers_dict.items():
        try:
            # Get the data for the past week
            data = yf.download(ticker, period='1wk', progress=False)
            
            if data.empty:
                performance_dict[name] = 'No data'
                continue

            # Get the last available close price
            close_price = data['Close'][-1]

            # Get the close price from a week ago
            week_ago_price = data['Close'][0]

            # Calculate the percentage change
            percentage_change = ((close_price - week_ago_price) / week_ago_price) * 100

            # Store the percentage change in the performance dictionary
            performance_dict[name] = percentage_change

        except Exception as e:
            performance_dict[name] = f"Error: {e}"

    return performance_dict


# Load the current tickers from the JSON file
with open('current_tickers.json', 'r') as file:
    current_tickers_dict = json.load(file)

# Get the weekly performance
weekly_performance = get_weekly_performance(current_tickers_dict)

# Sort the performance dictionary by performance
sorted_weekly_performance = dict(sorted(weekly_performance.items(), key=lambda item: item[1], reverse=True))

# Get the top 5 and bottom 5 performers
sorted_items = list(sorted_weekly_performance.items())
top_5 = sorted_items[-5:]
bottom_5 = sorted_items[:5]

with open('weekly_performance.txt','w') as file:
    for ticker, performance in sorted_weekly_performance.items():
        file.write(f"{ticker}: {performance}\n")
# Print the results
print(f"Full perfoarmance: {sorted_weekly_performance}")
# print(f"Top 5 performers of the week: {top_5}")
# print(f"Bottom 5 performers of the week: {bottom_5}")

