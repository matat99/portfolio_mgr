# data_retrieval.py

import requests
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import DateOffset
import json
import time
from requests.exceptions import RequestException

api_key = "42c83d3d0b0e24c532ce1cd511d95724" # They key is hard-coded... I know it's bad practice FUCK YOU 


def get_eur_exchange_rates(api_key):
    """Fetch exchange rates for 1 EUR to other currencies."""
    target_currencies = ["GBP", "USD", "CAD"]
    url = f"http://api.exchangeratesapi.io/latest?base=EUR&symbols={','.join(target_currencies)}&access_key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['rates']


def calculate_position_values_with_currency_adjustment(transactions_dict, current_tickers, downloaded_data, eur_rates):
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

            current_value_in_stock_currency = total_shares * data['Close'].loc["2023-05-31"] #<- specific cutoff | data['Close'].iloc[-1] <- last close date
            
            # Convert to GBP using the EUR as a pivot
            if currency != 'GBP':
                to_eur_rate = 1 / eur_rates[currency] if currency in eur_rates else 1  # If EUR, this rate will be 1
                current_value_in_eur = current_value_in_stock_currency * to_eur_rate
                current_value_in_gbp = current_value_in_eur * eur_rates['GBP']
            else:
                current_value_in_gbp = current_value_in_stock_currency

            position_values[name] = current_value_in_gbp
            total_portfolio_value += current_value_in_gbp

        except Exception as e:
            position_values[name] = f"Error: {e}"

    position_values['Total Portfolio'] = total_portfolio_value
    return position_values


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

    df = pd.DataFrame(weekly_performance_dict.items(), columns=['Company Name', 'Weekly Performance (%)'])
    df.to_csv('weekly_performance.csv', index=False)
    return df


def yearly_performance_June2June(transactions_dict, data_dict, name_to_ticker_map):
    yearly_performance_dict = {}

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
        
        # Limit the data to the range from June 2022 to June 2023
        data = data['2022-06-01':'2023-06-30']

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

        try:
            recent_price = data['Close'].loc['2023-06-01']
        except:
            recent_price = data['Close'].iloc[-1]

        try:
            one_year_ago_price = data['Close'].loc['2022-05-31']
        except:
            one_year_ago_price = data['Close'].iloc[0]

        start_value += total_shares * one_year_ago_price
        end_value += total_shares * recent_price

        stock_yearly_performance = ((recent_price - one_year_ago_price) / one_year_ago_price) * 100
        yearly_performance_dict[name] = round(stock_yearly_performance, 2)

    portfolio_yearly_performance = ((end_value - start_value) / start_value) * 100
    yearly_performance_dict['Total Portfolio'] = round(portfolio_yearly_performance, 2)

    df = pd.DataFrame(yearly_performance_dict.items(), columns=['Company Name', 'Yearly Performance (%)'])
    df.to_csv('yearly_performance_new.csv', index=False)
    return df


def yearly_performance_YoY(transactions_dict, data_dict, name_to_ticker_map):
    yearly_performance_dict = {}

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

        # Getting the close from approximately 252 trading days ago (assuming 252 trading days in a year)
        one_year_ago_index = -253 if len(data) >= 253 else -len(data)
        one_year_ago_price = data['Close'].iloc[one_year_ago_index]

        start_value += total_shares * one_year_ago_price
        end_value += total_shares * recent_price

        stock_yearly_performance = ((recent_price - one_year_ago_price) / one_year_ago_price) * 100
        yearly_performance_dict[name] = round(stock_yearly_performance, 2)

    portfolio_yearly_performance = ((end_value - start_value) / start_value) * 100
    yearly_performance_dict['Total Portfolio'] = round(portfolio_yearly_performance, 2)

    df = pd.DataFrame(yearly_performance_dict.items(), columns=['Company Name', 'Yearly Performance (%)'])
    df.to_csv('yearly_performance.csv', index=False)
    return df


def calculate_overall_performance(transactions_dict, data_dict, name_to_ticker_map, current_portfolio_value):
    performance_dict = {}

    cutoff_date = pd.to_datetime("2023-05-31")

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
        #recent_price = data['Close'].iloc[-1] # <- This is for last close
        recent_price = data.loc[cutoff_date, 'Close']

        # Calculate percentage change for the stock
        percentage_change = ((recent_price - purchase_price) / purchase_price) * 100
        performance_dict[name] = round(percentage_change, 2)

    # Calculate overall performance of the fund
    starting_fund_value = 10000
    fund_percentage_change = ((current_portfolio_value - starting_fund_value) / starting_fund_value) * 100
    performance_dict["Overall Fund Performance"] = round(fund_percentage_change, 2)

    # Convert dictionary to DataFrame and save to CSV
    df = pd.DataFrame(performance_dict.items(), columns=['Company Name', 'Performance (%)'])
    df.to_csv('overall_performance.csv', index=False)
    return df


def weekly_portfolio_performance_with_currency_adjustment(transactions_data, downloaded_fx, downloaded_data):
    weekly_values = {}

    currency_mapping = {
        '': 'USD',
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',
        '.F': 'EUR'
    }

    all_dates = [pd.to_datetime(trans['date']) for ticker_trans in transactions_data.values() for trans in ticker_trans]
    start_date = min(all_dates)
    end_date = pd.to_datetime('2023-05-31')

    # Generate a list of week ends (Fridays) between start_date and end_date
    week_ends = pd.date_range(start_date, end_date, freq='W-FRI')

    # A dictionary to cache exchange rates at the start of each month
    monthly_exchange_rates = downloaded_fx

    # Check for missing data before main loop
    for week_end in week_ends:
        missing_tickers = [ticker for ticker, data in downloaded_data.items() if week_end not in data.index]
        if missing_tickers:
            print(f"Missing data for date {week_end} for tickers: {', '.join(missing_tickers)}")

    for week_end in week_ends:
        weekly_total = 0.0

        for ticker, transactions in transactions_data.items():
            transactions = transactions_data.get(ticker, [])

            if not transactions:
                continue

            try:
                data = downloaded_data[ticker]
                suffix = ticker.split('.')[-1] if '.' in ticker else ''
                currency = currency_mapping.get('.' + suffix, 'USD')

                total_shares = 0.0
                for transaction in transactions:
                    transaction_date = pd.to_datetime(transaction['date'])
                    if transaction_date > week_end:
                        break
                    if transaction_date not in data.index:
                        continue

                    if transaction['amount'] > 0:
                        shares_bought = transaction['amount'] / data.loc[transaction_date, 'Close']
                        total_shares += shares_bought
                    else:
                        shares_sold = -transaction['amount'] / data.loc[transaction_date, 'Close']
                        total_shares -= shares_sold

                current_value_in_stock_currency = total_shares * data['Close'].loc[week_end]

                # Get the currency exchange rate for the current month
                month_start = week_end.replace(day=1)
                current_exchange_rates = monthly_exchange_rates[month_start]

                # Convert to GBP using the EUR as a pivot
                if currency != 'GBP':
                    to_eur_rate = 1 / current_exchange_rates[currency] if currency in current_exchange_rates else 1
                    current_value_in_eur = current_value_in_stock_currency * to_eur_rate
                    current_value_in_gbp = current_value_in_eur * current_exchange_rates['GBP']
                else:
                    current_value_in_gbp = current_value_in_stock_currency

                weekly_total += current_value_in_gbp

            except Exception as e:
                print(f"Error processing {ticker}: {e}")

        weekly_values[week_end] = weekly_total

    # Convert the dictionary to a DataFrame and save to CSV
    df = pd.DataFrame(weekly_values.items(), columns=['Date', 'Portfolio Value'])
    df.to_csv('weekly_portfolio_performance_with_currency_adjustment.csv', index=False)

    return df








