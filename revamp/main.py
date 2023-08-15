# main.py

from datetime import datetime
import os

from utilities import load_dict_from_json, save_to_csv
from data_retrieval import calculate_position_values
from data_download import get_earliest_transaction_year, download_data_for_tickers


if __name__ == "__main__":

    # Load Transactions and current tickers

    transaction_data = load_dict_from_json('../transactions.json')

    current_tickers = load_dict_from_json('../current_tickers.json')
    
    print(type(transaction_data))

    # Download all the data

    downloaded_data = download_data_for_tickers(transaction_data)

    # Value of our current positions 

    value = calculate_position_values(transaction_data, current_tickers, downloaded_data)

    save_to_csv(value, current_tickers)

    print(value)
    
