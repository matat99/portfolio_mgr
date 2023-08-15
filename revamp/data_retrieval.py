# data_retrieval.py

import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import DateOffset

def calculate_position_values(transactions_dict, current_tickers, downloaded_data):
    position_values = {}

    # Only process tickers that are currently in the portfolio
    for ticker in current_tickers.values():
        transactions = transactions_dict.get(ticker, [])

        # If there are no transactions for a ticker, its value is 0
        if not transactions:
            position_values[ticker] = 0.0
            continue

        try:
            data = downloaded_data[ticker]

            total_shares = 0.0
            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                
                # Ensure the date is within the available data range
                if transaction_date not in data.index:
                    print(f"Date {transaction_date} not available for {ticker}. Skipping this transaction.")
                    continue
                
                print(f"Using data for {ticker} on {transaction_date}.")
                
                if transaction['amount'] > 0:  # Buying
                    shares_bought = transaction['amount'] / data.loc[transaction_date, 'Close']
                    total_shares += shares_bought
                else:  # Selling
                    shares_sold = -transaction['amount'] / data.loc[transaction_date, 'Close']
                    total_shares -= shares_sold

            # Calculate the current value of the position based on current stock price and total shares
            position_values[ticker] = total_shares * data['Close'].iloc[-1]

        except Exception as e:
            position_values[ticker] = f"Error: {e}"

    return position_values






