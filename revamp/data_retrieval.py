# data_retrieval.py

import requests
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import DateOffset
import json
import time
from requests.exceptions import RequestException
import openpyxl
import pickle

currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }

def calculate_position_values_with_currency_adjustment(transactions_dict, current_tickers, downloaded_data, fx_rates):
    position_values = {}
    total_portfolio_value = 0

    # Fetch EUR exchange rates to other major currencies
    eur_rates = fx_rates

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
        
        if not transactions:
            continue

        try:
            data = downloaded_data[ticker]
            suffix = ticker.split('.')[-1] if '.' in ticker else ''
            currency = currency_mapping.get('.' + suffix, 'USD')

            total_shares = 0.0
            for transaction in transactions:
                # Directly add or subtract shares based on the transaction
                total_shares += transaction['shares']

                # Check the 'sold' flag
                if 'sold' in transaction and transaction['sold']:
                    # If the position is fully sold, stop tracking this stock
                    break

            if total_shares <= 0:
                # Skip calculation if all shares are sold or if the number of shares is negative
                continue

            current_value_in_stock_currency = total_shares * data['Close'].iloc[-1]
            
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

            # Check the 'sold' flag
            if 'sold' in transaction and transaction['sold']:
                # If the position is fully sold, disregard this position
                total_shares = 0
                break

            # Adjust total shares based on the transaction
            total_shares += transaction['shares']

        if total_shares == 0:
            # If all shares are sold or if the position is to be disregarded, continue to the next stock
            continue

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


def calculate_total_dividends(transactions_dict, historical_data, fx_rates):
    """
    Calculate the total dividends received from each position in GBP,
    stopping once the position is fully sold.

    :param transactions_dict: Dictionary containing transactions for each stock.
    :param historical_data: Dictionary containing historical data for each stock, including dividends.
    :param fx_rates: Dictionary of exchange rates with EUR as the base.
    :param currency_mapping: Dictionary mapping stock tickers to their respective currencies.
    :return: Dictionary of total dividends received for each stock in GBP.
    """

    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }

    total_dividends_gbp = {}
    sum_of_all_dividends = 0

    for ticker, transactions in transactions_dict.items():
        if not transactions or ticker not in historical_data:
            continue

        current_shares = 0
        stock_dividends_gbp = 0
        position_sold = False

        # Determine the currency of the stock
        suffix = ticker.split('.')[-1] if '.' in ticker else ''
        currency = currency_mapping.get('.' + suffix, 'USD')

        # Sort transactions by date
        sorted_transactions = sorted(transactions, key=lambda x: x['date'])

        for date, row in historical_data[ticker].iterrows():
            # Update current shares and check for the sold flag
            while sorted_transactions and sorted_transactions[0]['date'] <= date.strftime('%Y-%m-%d'):
                transaction = sorted_transactions.pop(0)
                current_shares += transaction['shares']
                if 'sold' in transaction and transaction['sold']:
                    position_sold = True

            if position_sold:
                break  # Stop processing dividends if the position is sold

            # Add dividends if shares are held
            if current_shares > 0 and 'Dividends' in row and row['Dividends'] > 0:
                dividend_amount = row['Dividends'] * current_shares
                stock_dividends_gbp += convert_dividend_to_gbp(dividend_amount, currency, date, fx_rates)

        total_dividends_gbp[ticker] = stock_dividends_gbp
        sum_of_all_dividends += stock_dividends_gbp


    return total_dividends_gbp, sum_of_all_dividends


def convert_dividend_to_gbp(amount, currency, date, fx_rates):
    """
    Convert an amount from a given currency to GBP using EUR as a pivot.

    :param amount: Amount in the original currency.
    :param currency: Original currency of the amount.
    :param date: Date of the conversion for fetching the appropriate exchange rate.
    :param fx_rates: Dictionary of exchange rates with EUR as the base.
    :return: Converted amount in GBP.
    """
    if currency == 'GBP':
        return amount

    # Get the exchange rate to EUR for the given currency
    to_eur_rate = fx_rates.get(currency, 1)

    # Convert amount to EUR
    amount_in_eur = amount / to_eur_rate

    # Convert amount from EUR to GBP
    eur_to_gbp_rate = fx_rates.get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate


def load_exchange_rates(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def convert_to_gbp(amount, currency, date, exchange_rates):
    if currency == 'GBP':
        return amount  # No conversion needed for GBP

    # Get the exchange rate to EUR for the given currency
    to_eur_rate = exchange_rates[date].get(currency, 1)

    # Convert amount to EUR
    amount_in_eur = amount / to_eur_rate

    # Convert amount from EUR to GBP
    eur_to_gbp_rate = exchange_rates[date].get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate


def calculate_cash_position(transactions_dict, exchange_rates_file, historical_data, fx_rates):
    cash_position = 10000
    exchange_rates = load_exchange_rates(exchange_rates_file)
    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }

    for ticker, transactions in transactions_dict.items():
        suffix = ticker.split('.')[-1] if '.' in ticker else ''
        currency = currency_mapping.get('.' + suffix, 'USD')

        for transaction in transactions:
            # Use historical_data for share prices
            share_price = historical_data[ticker]['Close'].loc[transaction['date']]
            transaction_amount_gbp = convert_to_gbp(transaction['shares'] * share_price, currency, transaction['date'], exchange_rates)
            print(transaction_amount_gbp)
            print(transaction)
            
            # Subtract the transaction amount (buying subtracts, selling adds due to negative shares) 
            cash_position -= transaction_amount_gbp

    total_dividends_gbp = calculate_total_dividends(transactions_dict, historical_data, fx_rates)[1]
    print(total_dividends_gbp)
    cash_position += total_dividends_gbp

    return cash_position




