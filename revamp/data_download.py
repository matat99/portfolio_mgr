import yfinance as yf
import pandas as pd
import time 

def get_earliest_transaction_year(transactions_dict):
    years = {}
    for ticker, transactions in transactions_dict.items():
        if transactions:  # Check if transactions list is not empty
            dates = [pd.to_datetime(transaction['date']) for transaction in transactions]
            earliest_year = min(dates).year
            years[ticker] = earliest_year
    return years


def download_data_for_tickers(tickers, retries=3, delay=5):
    data_dict = {}
    for ticker in tickers:
        for i in range(retries):
            try:
                data = yf.download(ticker, progress=False)
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
    return data_dict
