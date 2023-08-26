import yfinance as yf
import time
import pandas as pd
import pickle
import requests

def download_data_for_tickers(tickers, retries=3, delay=5, save_to_file=True):
    data_dict = {}
    start_date = pd.to_datetime("2017-01-01")
    end_date = pd.to_datetime("2023-05-31")  # To get data up to today

    for ticker in tickers:
        for i in range(retries):
            try:
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                data_dict[ticker] = data
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
        with open("downloaded_data.pkl", "wb") as f:
            pickle.dump(data_dict, f)

    return data_dict

def load_saved_data(file_name="downloaded_data.pkl"):
    with open(file_name, "rb") as f:
        data_dict = pickle.load(f)
    return data_dict


def download_exchange_rates(api_key, start_date='2017-12-01', end_date='2023-05-01', retries=3, delay=5, save_to_file=True):
    # Generate monthly dates for exchange rates
    month_starts = pd.date_range(start_date, end_date, freq='MS')

    data_dict = {}

    # Target currencies
    target_currencies = ["GBP", "USD", "CAD"]

    for date in month_starts:
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
        with open("exchange_rates_data.pkl", "wb") as f:
            pickle.dump(data_dict, f)

    return data_dict


def load_saved_exchange_rates(file_name="exchange_rates_data.pkl"):
    with open(file_name, "rb") as f:
        data_dict = pickle.load(f)
    return data_dict

