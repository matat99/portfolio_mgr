# data_retrieval.py

import requests
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import DateOffset
import json
import time
from requests.exceptions import RequestException
from data_download import download_weekly_exchange_rates
import openpyxl


api_key = "42c83d3d0b0e24c532ce1cd511d95724" # The key is hard-coded... I know it's bad practice


def get_eur_exchange_rates(api_key):
    """Fetch exchange rates for 1 EUR to other currencies."""
    target_currencies = ["GBP", "USD", "CAD"]
    url = f"http://api.exchangeratesapi.io/latest?base=EUR&symbols={','.join(target_currencies)}&access_key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['rates']


def calculate_position_values_with_currency_adjustment(transactions_dict, current_tickers, downloaded_data):
    position_values = {}
    total_portfolio_value = 0

    # Fetch EUR exchange rates to other major currencies
    eur_rates = get_eur_exchange_rates(api_key)

    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }

    for name, ticker in current_tickers.items():
        transactions = transactions_dict.get(ticker, [])
        
        # If no transactions, move on.
        if not transactions:
            continue

        try:
            data = downloaded_data[ticker]

            # Determine the stock's currency using the mapping
            suffix = ticker.split('.')[-1] if '.' in ticker else ''
            currency = currency_mapping.get('.' + suffix, 'USD')

            total_shares = 0.0
            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                if transaction_date not in data.index:
                    continue
                
                if transaction['amount'] > 0:
                    shares_bought = transaction['amount'] / data.loc[transaction_date, 'Close']
                    total_shares += shares_bought
                    
                else:
                    shares_sold = -transaction['amount'] / data.loc[transaction_date, 'Close']
                    total_shares -= shares_sold
                    

            print(total_shares)
            current_value_in_stock_currency = total_shares * data['Close'].iloc[-1] #last close #data['Close'].loc["2022-06-01"]
            
            # Convert to GBP using the EUR as a pivot
            if currency != 'GBP':
                to_eur_rate = 1 / eur_rates.get(currency, 1)
                current_value_in_eur = current_value_in_stock_currency * to_eur_rate
                current_value_in_gbp = current_value_in_eur * eur_rates.get('GBP', 1)
            else:
                current_value_in_gbp = current_value_in_stock_currency

            position_values[name] = current_value_in_gbp
            total_portfolio_value += current_value_in_gbp

        except Exception as e:
            position_values[name] = f"Error: {e}"

    position_values['Total Portfolio'] = total_portfolio_value
    

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(position_values.items()), columns=['Company Name', 'Position Value (GBP)'])
    
    return df


def weekly_performance(transactions_dict, data_dict, name_to_ticker_map):
    weekly_performance_dict = {}

    end_value = 0.0
    start_value = 0.0

    for name, ticker in name_to_ticker_map.items():
        transactions = transactions_dict.get(ticker, [])
        if not transactions:
            continue

        data = data_dict.get(ticker)
        if data is None:
            print(f"Data not available for {ticker}. Skipping...")
            continue

        total_shares = 0.0
        for transaction in transactions:
            transaction_date = pd.to_datetime(transaction['date'])
            if transaction_date not in data.index:
                continue
                
            if transaction['amount'] > 0:
                shares_bought = transaction['amount'] / data.loc[transaction_date, 'Close']
                total_shares += shares_bought
            else:
                shares_sold = -transaction['amount'] / data.loc[transaction_date, 'Close']
                total_shares -= shares_sold

        recent_price = data['Close'].iloc[-1]

        # Getting the close from 5 trading days ago
        one_week_ago_index = -6 if len(data) >= 6 else -len(data)
        one_week_ago_price = data['Close'].iloc[one_week_ago_index]

        start_value += total_shares * one_week_ago_price
        end_value += total_shares * recent_price

        stock_weekly_performance = ((recent_price - one_week_ago_price) / one_week_ago_price) * 100
        weekly_performance_dict[name] = round(stock_weekly_performance, 2)

    portfolio_weekly_performance = ((end_value - start_value) / start_value) * 100
    weekly_performance_dict['Total Portfolio'] = round(portfolio_weekly_performance, 2)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(weekly_performance_dict.items(), columns=['Company Name', 'Weekly Performance (%)'])
    
    # Return the DataFrame
    return df


def calculate_overall_performance(transactions_dict, data_dict, name_to_ticker_map, current_portfolio_value, cutoff_date=None):
    performance_dict = {}

    # Use the latest data if no cutoff_date is provided
    if cutoff_date is not None:
        cutoff_date = pd.to_datetime(cutoff_date)
    
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

        # Get close price on purchase date
        purchase_price = data.loc[first_transaction_date, 'Close']

        # If a cutoff_date is provided, use it; otherwise, use the last available close price
        recent_price = data.loc[cutoff_date, 'Close'] if cutoff_date is not None else data['Close'].iloc[-1]

        # Calculate percentage change for the stock
        percentage_change = ((recent_price - purchase_price) / purchase_price) * 100
        performance_dict[name] = round(percentage_change, 2)

    # Calculate overall performance of the fund
    starting_fund_value = 10000  
    fund_percentage_change = ((current_portfolio_value - starting_fund_value) / starting_fund_value) * 100
    performance_dict["Total Portfolio"] = round(fund_percentage_change, 2)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(performance_dict.items(), columns=['Company Name', 'Performance (%)'])
    # Optionally, you could save to CSV based on a condition or argument

    # Return the DataFrame
    return df

