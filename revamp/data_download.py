import yfinance as yf
import time
import pandas as pd
import pickle
import requests

import yfinance as yf
import pandas as pd
import time
import pickle

def download_data_for_tickers(tickers, retries=3, delay=5, save_to_file=True, file_path="downloaded_data.pkl"):
    data_dict = {}
    start_date = pd.to_datetime("2017-12-01")

    for ticker in tickers:
        for i in range(retries):
            try:
                # Download the historical market data
                market_data = yf.download(ticker, start=start_date, progress=False)
                
                # Remove timezone information from market data
                market_data.index = market_data.index.tz_localize(None)

                # Use yf.Ticker to get the dividend data
                ticker_data = yf.Ticker(ticker)
                dividend_data = ticker_data.dividends
                
                # Remove timezone information from div data
                dividend_data.index = dividend_data.index.tz_localize(None)

                # Reindex the dividend data to match the market data's dates
                dividend_data = dividend_data.reindex(market_data.index).fillna(0)

                # Combine market data and dividend data
                combined_data = market_data.join(dividend_data, how='outer')

                # Assuming success, store the data in the dictionary
                data_dict[ticker] = combined_data
                print(f"Data for {ticker} downloaded successfully with latest date: {combined_data.index[-1].date()}")
                break
            except Exception as e:
                print(f"Error downloading data for {ticker}: {e}")
                if i < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to download data for {ticker} after {retries} retries.")
        time.sleep(1)  # Introduce a 1-second delay between requests

    # Save to file if flag is set
    if save_to_file:
        with open(file_path, "wb") as f:
            pickle.dump(data_dict, f)

    return data_dict




def load_saved_data(file_name="downloaded_data.pkl"):
    with open(file_name, "rb") as f:
        data_dict = pickle.load(f)
    return data_dict


def download_weekly_exchange_rates(api_key, start_date='2023-08-21', end_date=None, retries=3, delay=5, save_to_file=True):
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    # Generate weekly dates for exchange rates
    week_starts = pd.date_range(start_date, end_date, freq='W')

    data_dict = {}

    # Target currencies
    target_currencies = ["GBP", "USD", "CAD"]

    for date in week_starts:
        date_str = date.strftime('%Y-%m-%d')
        
        # Construct the URL for each specific date
        url = f"http://api.exchangeratesapi.io/{date_str}?base=EUR&symbols={','.join(target_currencies)}&access_key={api_key}"

        for i in range(retries):
            try:
                response = requests.get(url)
                data = response.json()
                rates = data['rates']
                if rates:
                    data_dict[date_str] = rates
                break
            except Exception as e:
                print(f"Error downloading exchange rates for {date_str}: {e}")
                if i < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to download exchange rates for {date_str} after {retries} retries.")

    # Save to file if flag is set
    if save_to_file:
        with open("weekly_exchange_rates_data.pkl", "wb") as f:
            pickle.dump(data_dict, f)

    return data_dict


def load_saved_exchange_rates(file_name="exchange_rates_data.pkl"):
    with open(file_name, "rb") as f:
        data_dict = pickle.load(f)
    return data_dict

