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


def weekly_performance(data_dict, current_tickers, filename='weekly.csv'):
    """
    Calculate the weekly performance for a list of tickers based on their data.
    
    :param data_dict: Dictionary containing tickers as keys and their data as values.
    :param current_tickers: Dictionary of currently held tickers.
    :return: Sorted list of tickers based on their weekly performance.
    """
    performance = {}

    for name, ticker in current_tickers.items():
        if ticker not in data_dict:
            print(f"No data available for {name} ({ticker}). Skipping.")
            continue

        data = data_dict[ticker]
        
        try:
            # Extract the last available close price
            last_close = data['Close'].iloc[-1]
            
            # Try to get the close price from exactly 7 days earlier
            # If not available, skip to the closest available previous date
            one_week_ago_date = data.index[-1] - pd.Timedelta(days=7)
            one_week_ago_data = data[data.index <= one_week_ago_date].tail(1)

            # If there's no data from a week ago, skip this ticker
            if one_week_ago_data.empty:
                print(f"Insufficient data for {name} ({ticker}) to compute weekly performance.")
                continue

            one_week_ago_close = one_week_ago_data['Close'].iloc[0]
            
            # Calculate percentage change
            change = ((last_close - one_week_ago_close) / one_week_ago_close) * 100
            formatted_change = f"{change:.2f}%"
            performance[name] = formatted_change

        except Exception as e:
            print(f"Error computing weekly performance for {name} ({ticker}): {e}")

    # Sort tickers based on performance
    sorted_performance = dict(sorted(performance.items(), key=lambda item: item[1], reverse=True))
    
    # saving to csv
    df = pd.DataFrame(sorted_performance.items(), columns=['Company Name', 'Weekly Performance'])
    df.to_csv(filename, index=False)



def calculate_overall_performance(transactions_dict, data_dict, name_to_ticker_map):
    performance_dict = {}

    for name, ticker in name_to_ticker_map.items():
        # Extract transactions for the ticker
        transactions = transactions_dict.get(ticker, [])

        # Get the date of the first transaction for the ticker
        if not transactions:
            continue
        first_transaction_date = pd.to_datetime(transactions[0]['date'])

        # Extract stock data for the ticker
        data = data_dict.get(ticker)

        # Handle case where data is not available
        if data is None or first_transaction_date not in data.index:
            print(f"Data not available for {ticker} on {first_transaction_date}. Skipping...")
            continue

        # Get close price on purchase date and the most recent close price
        purchase_price = data.loc[first_transaction_date, 'Close']
        recent_price = data['Close'].iloc[-1]

        # Calculate percentage change
        percentage_change = ((recent_price - purchase_price) / purchase_price) * 100
        performance_dict[name] = round(percentage_change, 2)

    # Convert dictionary to DataFrame and save to CSV
    df = pd.DataFrame(performance_dict.items(), columns=['Company Name', 'Performance (%)'])
    df.to_csv('overall_performance.csv', index=False)
    return df


