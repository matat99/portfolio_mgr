import yfinance as yf
import time
import pandas as pd
import pickle

def download_data_for_tickers(tickers, retries=3, delay=5, save_to_file=True):
    data_dict = {}
    start_date = pd.to_datetime("2017-01-01")
    end_date = pd.to_datetime("today")  # To get data up to today

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
