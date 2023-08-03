# IMPORTANT IMPORTANT for future reference NTT DO COMO: selling it we made 422.27 profit and got 74.35 in dividends

import yfinance as yf
import pandas as pd
import json
from datetime import date,timedelta
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import numpy as np

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def download_data(ticker, period='max'):
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            return 'No Data'
        else:
            return data
    except Exception as e:
        return f'Error: {e}'

def process_ticker(name, ticker, operation, start_date=None, end_date=None, full_data=False):
    # Download the max available data
    data = download_data(ticker, period='max')

    if isinstance(data, str):
        # This means if there was an error in the data
        return data

    # If full_data is True, pass the entire data to the operation function
    # Otherwise, pass only the data between start_date and end_date
    if full_data:
        return operation(name, data, start_date, end_date)
    else:
        return operation(data.loc[start_date:end_date], start_date, end_date)


def get_weekly_performance(tickers_dict, start_date, end_date):


    def operation(data, start_date, end_date):
        # Get only the data between start_date and end_date
        data = data.loc[start_date:end_date]

        # Get the last available close price
        close_price = data['Close'][-1]

        # Get the close price from a week ago
        week_ago_price = data['Close'][0]

        percentage_change = ((close_price - week_ago_price) / week_ago_price) * 100

        return round(percentage_change, 2)
        

    performance_dict = {name: process_ticker(name, ticker, operation, start_date, end_date) for name, ticker in tickers_dict.items()}


    return performance_dict


def get_position_worth(tickers_dict, transactions_dict):

    position_worth_dict = {}

    def operation(name, data, start_date=None, end_date=None):

        transactions = transactions_dict.get(name, [])

        # variable to store the total worth
        total_worth = 0.0

        for transaction in transactions:

            transaction_date = pd.to_datetime(transaction['date'])
            transaction_amount = transaction['amount']

            transaction_price = data.loc[transaction_date, 'Close']

            shares_bought = transaction_amount / transaction_price

            close_price = data['Close'][-1]

            worth = shares_bought * close_price

            total_worth += worth

        return total_worth

    position_worth_dict = {name: process_ticker(name, ticker, operation, full_data=True) for name, ticker in tickers_dict.items()}

    return position_worth_dict 

def main():
    # Load JSON files
    tickers_dict = load_json('current_tickers.json')
    transactions_dict = load_json('transactions.json')

    end_date = pd.Timestamp.now().floor('D')
    start_date = end_date - BDay(7)

    performance_dict = get_weekly_performance(tickers_dict, start_date, end_date)

    sorted_performance = {k: v for k, v in sorted(performance_dict.items(), key=lambda item: item[1], reverse=True)}

    with open('weekly_performance.txt', 'w') as file:
        for key, value in sorted_performance.items():
            if isinstance(value, float):
                file.write(f"{key}: {value:.2f}\n")
            else:
                file.write(f"{key}: {value}\n") 


    position_worth_dict = get_position_worth(tickers_dict, transactions_dict)

    position_worth_dict['Cash'] = 499.06

    labels = position_worth_dict.keys()
    sizes = position_worth_dict.values()

    plt.axis('equal')
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title('Portfolio Distribution')
    plt.show()

if __name__ == "__main__":
    main()