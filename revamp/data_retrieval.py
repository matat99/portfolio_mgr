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

            current_value_in_stock_currency = total_shares * data['Close'].loc["2022-06-01"] #data['Close'].iloc[-1] last close
            
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
    week_ends = pd.date_range(start_date, end_date, freq='W-FRI')
    monthly_exchange_rates = downloaded_fx

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

                # If week_end data is missing, get the closest previous date available
                if week_end not in data.index:
                    available_dates = data.index
                    previous_dates = available_dates[available_dates < week_end]
                    if previous_dates.empty:
                        print(f"No available previous data for {ticker} on {week_end}")
                        continue
                    last_available_date = previous_dates[-1]
                else:
                    last_available_date = week_end

                current_value_in_stock_currency = total_shares * data['Close'].loc[last_available_date]

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

    df = pd.DataFrame(weekly_values.items(), columns=['Date', 'Portfolio Value'])
    df.to_csv('weekly_portfolio_performance_with_currency_adjustment.csv', index=False)

    return df


def calculate_total_portfolio_value_as_of_date(transactions_dict, downloaded_data, eur_rates, date=None):
    total_portfolio_value = 0
    original_date = pd.to_datetime(date)

    if original_date:
        adjusted_date = original_date.replace(day=1)
        eur_rates = eur_rates.get(adjusted_date.strftime('%Y-%m-%d'), None)

    currency_mapping = {
        '': 'USD',
        '.L': 'GBP',
        '.DE': 'EUR',
        '.PA': 'EUR',
        '.TO': 'CAD',
        '.F': 'EUR'
    }

    for ticker, transactions in transactions_dict.items():
        if not transactions:
            continue

        total_shares = 0.0
        fully_sold = False

        try:
            data = downloaded_data[ticker]
            
            if original_date:
                latest_data = data.loc[:original_date]
                if latest_data.empty or original_date not in latest_data.index:
                    latest_data = latest_data.iloc[-1:] if not latest_data.empty else latest_data
            else:
                latest_data = data

            if latest_data.empty:
                continue
            
            latest_close = latest_data['Close'].iloc[-1]
            suffix = ticker.split('.')[-1] if '.' in ticker else ''
            currency = currency_mapping.get('.' + suffix, 'USD')

            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                print(type(transaction_date))


                
                if transaction_date > latest_data.index[-1]:
                    continue
                
                if fully_sold:
                    break

                if 'sold' in transaction and transaction['sold'] == True:
                    fully_sold = True

                if not fully_sold:
                    if transaction['amount'] > 0:
                        shares_bought = transaction['amount'] / latest_data.loc[transaction_date, 'Close']
                        total_shares += shares_bought
                    else:
                        shares_sold = -transaction['amount'] / latest_data.loc[transaction_date, 'Close']
                        total_shares -= shares_sold

            current_value_in_stock_currency = total_shares * latest_close

            if currency != 'GBP':
                to_eur_rate = 1 / eur_rates.get(currency, 1)
                current_value_in_eur = current_value_in_stock_currency * to_eur_rate
                current_value_in_gbp = current_value_in_eur * eur_rates.get('GBP', 1)
            else:
                current_value_in_gbp = current_value_in_stock_currency

            if not fully_sold:
                total_portfolio_value += current_value_in_gbp

        except Exception as e:
            print(f"Error calculating value for {ticker}: {e}")

    return total_portfolio_value





