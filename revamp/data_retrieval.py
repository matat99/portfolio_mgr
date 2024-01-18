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
import matplotlib.pyplot as plt

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


import pandas as pd

def calculate_daily_portfolio_values(transactions, historical_stock_data, exchange_rates):
    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }

    # Extract transaction dates and convert them to Timestamp objects
    all_transaction_dates = [pd.to_datetime(tx['date']) for txlist in transactions.values() for tx in txlist]
    
    # Determine the earliest transaction date
    start_date = min(all_transaction_dates)

    # Find the latest date available in historical stock data
    end_date = min([historical_stock_data[ticker].index.max() for ticker in transactions if ticker in historical_stock_data])

    # Initialize a DataFrame to store daily values
    date_range = pd.date_range(start_date, end_date)
    portfolio_values = pd.DataFrame(index=date_range)

    for ticker, txlist in transactions.items():
        suffix = ticker.split('.')[-1] if '.' in ticker else ''
        currency = currency_mapping.get('.' + suffix, 'USD')
        stock_data = historical_stock_data.get(ticker, pd.DataFrame())

        for single_date in date_range:
            # Forward fill for weekends and non-trading days
            if single_date not in stock_data.index and not stock_data.empty:
                last_available_date = stock_data.index[stock_data.index < single_date].max()
                stock_data = stock_data.reindex(date_range, method='ffill')
            stock_value = calculate_stock_value(ticker, txlist, stock_data, exchange_rates, single_date, currency_mapping)
            portfolio_values.at[single_date, ticker] = stock_value

    # Sum up values across each row and add as a new column
    portfolio_values['Total Portfolio Value'] = portfolio_values.sum(axis=1)

    return portfolio_values.fillna(0)


def calculate_stock_value(ticker, transactions, historical_data, exchange_rates, date, currency_mapping):
    total_shares = 0
    position_sold = False

    # Determine the stock's currency using the mapping
    suffix = ticker.split('.')[-1] if '.' in ticker else ''
    currency = currency_mapping.get('.' + suffix, 'USD')

    for transaction in transactions:
        transaction_date = pd.to_datetime(transaction['date'])
        if transaction_date <= date:
            if 'sold' in transaction and transaction['sold']:
                position_sold = True
                break
            total_shares += transaction['shares']

    
    #print(f"Ticker: {ticker}, Date: {date}, Total Shares: {total_shares}, Position Sold: {position_sold}")

    if position_sold or total_shares <= 0:
        return 0  # Position is closed or no shares held

    if date in historical_data.index:
        close_price = historical_data.loc[date, 'Close']
        stock_value = total_shares * close_price

        # Convert the value to GBP using exchange rates
        if currency != 'GBP':
            to_eur_rate = exchange_rates[date.strftime("%Y-%m-%d")].get(currency, 1)
            amount_in_eur = stock_value / to_eur_rate
            eur_to_gbp_rate = exchange_rates[date.strftime("%Y-%m-%d")].get('GBP', 1)
            return amount_in_eur * eur_to_gbp_rate
        else:
            return stock_value
    else:
        return 0  # No data for the given date


# Example usage
# Load your data (transaction_data, historical_stock_data, exchange_rates)
# transaction_data = {'BLK': [{"date":"2020-12-30", "shares":2}], ...}
# historical_stock_data = {'BLK': DataFrame_of_BLK_stock_data, ...}
# exchange_rates = { ... }  # Loaded from exchange_rates.pkl
# currency_mapping = {...}
# daily_values_df = calculate_daily_portfolio_values(transaction_data, historical_stock_data, exchange_rates, currency_mapping)


def calculate_daily_dividends(transactions, historical_stock_data, exchange_rates):
    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }
    # Convert transaction dates to Timestamps and find the earliest transaction date
    all_transaction_dates = [pd.to_datetime(tx['date']) for txlist in transactions.values() for tx in txlist]
    start_date = min(all_transaction_dates)

    # Find the latest date in the historical stock data
    end_date = max([stock_data.index.max() for stock_data in historical_stock_data.values()])

    # Initialize a DataFrame to store daily dividend values with 0.0 (float) as default
    date_range = pd.date_range(start_date, end_date)
    dividend_values = pd.DataFrame({'Date': date_range, 'Dividends GBP': 0.0})  # Use 0.0 to set dtype as float

    # Iterate through each day within the date range
    for single_date in date_range:
        total_dividends_gbp = 0.0

        for ticker, stock_data in historical_stock_data.items():
            if single_date in stock_data.index and stock_data.loc[single_date, 'Dividends'] > 0:
                # Determine the stock's currency
                suffix = ticker.split('.')[-1] if '.' in ticker else ''
                currency = currency_mapping.get('.' + suffix, 'USD')

                total_shares = calculate_total_shares_held(transactions.get(ticker, []), single_date)
                dividend_amount = total_shares * stock_data.loc[single_date, 'Dividends']
                dividend_gbp = convert_dividend_to_gbp(dividend_amount, currency, single_date, exchange_rates)

                total_dividends_gbp += dividend_gbp

        # Update the dividend value for the day
        if total_dividends_gbp > 0:
            dividend_values.loc[dividend_values['Date'] == single_date, 'Dividends GBP'] = total_dividends_gbp

    return dividend_values

# Rest of the functions remain the same




def calculate_total_shares_held(transactions, date):
    total_shares = 0
    for transaction in transactions:
        transaction_date = pd.to_datetime(transaction['date'])
        if transaction_date <= date:
            total_shares += transaction['shares']
    return total_shares

def convert_dividend_to_gbp(amount, currency, date, exchange_rates):
    if currency == 'GBP':
        return amount  # No conversion needed for GBP

    # Get the exchange rate to EUR for the given currency
    to_eur_rate = exchange_rates[date.strftime("%Y-%m-%d")].get(currency, 1)

    # Convert amount to EUR
    amount_in_eur = amount / to_eur_rate

    # Convert amount from EUR to GBP
    eur_to_gbp_rate = exchange_rates[date.strftime("%Y-%m-%d")].get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate

# Example usage
# Load your data (transaction_data, historical_stock_data, exchange_rates, currency_mapping)
# daily_dividends = calculate_daily_dividends(transaction_data, historical_stock_data, exchange_rates, currency_mapping)



def calculate_daily_cash_position(transactions_dict, exchange_rates, historical_data):
    currency_mapping = {
        '': 'USD',     # Default to USD for NASDAQ and similar
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',   # Toronto Stock Exchange
        '.F': 'EUR'
    }
    initial_cash_position = 10000.0

    all_transaction_dates = [pd.to_datetime(tx['date']) for txlist in transactions_dict.values() for tx in txlist]
    start_date = min(all_transaction_dates)
    end_date = max([stock_data.index.max() for stock_data in historical_data.values()])

    daily_cash_positions = pd.DataFrame({'Date': pd.date_range(start_date, end_date), 'Cash Position GBP': initial_cash_position})

    for single_date in pd.date_range(start_date, end_date):
        daily_cash_change = 0.0

        for ticker, transactions in transactions_dict.items():
            suffix = ticker.split('.')[-1] if '.' in ticker else ''
            currency = currency_mapping.get('.' + suffix, 'USD')

            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                if transaction_date == single_date:
                    share_price = historical_data[ticker]['Close'].loc[transaction_date]
                    transaction_amount_gbp = convert_to_gbp_cash(transaction['shares'] * share_price, currency, transaction_date, exchange_rates)
                    daily_cash_change -= transaction_amount_gbp  # Subtracting both for buying and selling

        if single_date == start_date:
            daily_cash_positions.loc[daily_cash_positions['Date'] == single_date, 'Cash Position GBP'] = initial_cash_position + daily_cash_change
        else:
            prev_day_cash = daily_cash_positions.loc[daily_cash_positions['Date'] == single_date - pd.Timedelta(days=1), 'Cash Position GBP'].values[0]
            daily_cash_positions.loc[daily_cash_positions['Date'] == single_date, 'Cash Position GBP'] = prev_day_cash + daily_cash_change

    return daily_cash_positions


def convert_to_gbp_cash(amount, currency, date, exchange_rates):
    # Format the date to match the keys in the exchange_rates dictionary
    formatted_date = date.strftime("%Y-%m-%d")

    if currency == 'GBP':
        return amount  # No conversion needed for GBP

    # Get the exchange rate to EUR for the given currency
    to_eur_rate = exchange_rates.get(formatted_date, {}).get(currency, 1)

    # Convert amount to EUR
    amount_in_eur = amount / to_eur_rate

    # Convert amount from EUR to GBP
    eur_to_gbp_rate = exchange_rates.get(formatted_date, {}).get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate


import matplotlib.pyplot as plt

def combine_and_plot_data(portfolio_values_df, cash_position_df, dividends_df):
    # Reset index to convert the date index to a column
    portfolio_values_df = portfolio_values_df.reset_index().rename(columns={'index': 'Date'})

    # Combine the dataframes
    combined_df = portfolio_values_df.merge(cash_position_df, on='Date')
    combined_df = combined_df.merge(dividends_df, on='Date')

    # Calculate total portfolio value with and without dividends
    combined_df['Total Portfolio Value with Dividends'] = combined_df['Total Portfolio Value'] + combined_df['Cash Position GBP'] + combined_df['Dividends GBP']
    combined_df['Total Portfolio Value without Dividends'] = combined_df['Total Portfolio Value'] + combined_df['Cash Position GBP']

    # Plotting
    plt.figure(figsize=(15, 7))

    # Plot for total portfolio value without dividends
    plt.subplot(1, 2, 1)
    plt.plot(combined_df['Date'], combined_df['Total Portfolio Value without Dividends'], label='Without Dividends', color='blue')
    plt.title('Total Portfolio Value Over Time Without Dividends')
    plt.xlabel('Date')
    plt.ylabel('Value in GBP')
    plt.legend()

    # Plot for total portfolio value with dividends
    plt.subplot(1, 2, 2)
    plt.plot(combined_df['Date'], combined_df['Total Portfolio Value with Dividends'], label='With Dividends', color='green')
    plt.title('Total Portfolio Value Over Time With Dividends')
    plt.xlabel('Date')
    plt.ylabel('Value in GBP')
    plt.legend()

    plt.tight_layout()
    plt.show()

    return combined_df

# You would call this function with your dataframes like this:
# final_df = combine_and_plot_data(portfolio_values_df, cash_position_df, dividends_df)





