import requests
import pickle
import os
import time
from datetime import datetime, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def fetch_and_save_exchange_rates(api_key, start_date, end_date, base_currency, file_path):
    api_url = "http://api.exchangeratesapi.io/v1/"
    exchange_rates = {}

    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            exchange_rates = pickle.load(file)

    total_days = (end_date - start_date).days
    days_processed = 0

    for single_date in daterange(start_date, end_date):
        formatted_date = single_date.strftime("%Y-%m-%d")
        response = requests.get(f"{api_url}{formatted_date}?access_key={api_key}&base={base_currency}")

        if response.status_code == 200:
            data = response.json()
            exchange_rates[formatted_date] = data.get("rates", {})
            days_processed += 1
            print(f"Downloaded data for {formatted_date}. Progress: {days_processed}/{total_days}")

            # Save the data to a pickle file after each successful request
            with open(file_path, 'wb') as file:
                pickle.dump(exchange_rates, file)
        else:
            print(f"Failed to fetch data for {formatted_date}: HTTP {response.status_code}")

        time.sleep(1)  # Wait for 1 second before the next request

def fetch_exchange_rates_in_chunks(api_keys, start_date, end_date, base_currency, file_path):
    chunk_size = 990
    total_days = (end_date - start_date).days
    for i in range(0, total_days, chunk_size):
        chunk_start = start_date + timedelta(days=i)
        chunk_end = min(chunk_start + timedelta(days=chunk_size), end_date)
        api_key = api_keys[i // chunk_size % len(api_keys)]
        fetch_and_save_exchange_rates(api_key, chunk_start, chunk_end, base_currency, file_path)

# Example usage
api_keys = ["8605a82e02a21c79234296dd217baa0d", "d03752bb2df9c6e7406e4d517d292b23", "bea8b0447789aa42c00c0a8774110b28"]  # List of API keys
start = datetime(2017, 12, 1)
end = datetime(2024, 1, 16)
base = "EUR"
file_path = "exchange_rates.pkl"

fetch_exchange_rates_in_chunks(api_keys, start, end, base, file_path)
