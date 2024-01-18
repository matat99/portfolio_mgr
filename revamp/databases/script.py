#script.py

import requests
import pickle
import os
import time
from datetime import datetime, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def fetch_and_save_exchange_rates(api_key, base_currency, file_path):
    api_url = "http://api.exchangeratesapi.io/v1/"
    exchange_rates = {}
    today = datetime.now().date()

    # Load existing data if file exists and find the last date fetched
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            exchange_rates = pickle.load(file)
            last_date_fetched = datetime.strptime(max(exchange_rates), '%Y-%m-%d').date() if exchange_rates else None
    else:
        last_date_fetched = None

    # If the file is up to date, do nothing
    if last_date_fetched and last_date_fetched >= today:
        print(f"Exchange rates file is already up to date. \nLast available date: {last_date_fetched}")
        return

    # Determine the start date for fetching data
    start_date = last_date_fetched + timedelta(days=1) if last_date_fetched else datetime.today().date()

    for single_date in daterange(start_date, today):
        formatted_date = single_date.strftime("%Y-%m-%d")
        response = requests.get(f"{api_url}{formatted_date}?access_key={api_key}&base={base_currency}")

        if response.status_code == 200:
            data = response.json()
            exchange_rates[formatted_date] = data.get("rates", {})
            print(f"Downloaded data for {formatted_date}.")
            # Save the data to a pickle file after each successful request
            with open(file_path, 'wb') as file:
                pickle.dump(exchange_rates, file)
        else:
            print(f"Failed to fetch data for {formatted_date}: HTTP {response.status_code}")

        time.sleep(1)  # Wait for 1 second before the next request

# Example usage
api_key = "42c83d3d0b0e24c532ce1cd511d95724"  # Replace with your actual API key
base = "EUR"
file_path = "exchange_rates.pkl"

fetch_and_save_exchange_rates(api_key, base, file_path)

