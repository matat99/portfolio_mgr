# IMPORTANT IMPORTANT for future reference NTT DO COMO: selling it we made 422.27 profit and got 74.35 in dividends


import yfinance as yf
import pandas as pd
import json
from datetime import date,timedelta

# Load tickers from JSON file
with open('current_tickers.json', 'r') as file:
    tickers_dict = json.load(file)

# Load transactions from JSON file
with open('transactions.json', 'r') as file:
    transactions_dict = json.load(file)


portfolio_dict = {ticker: {'quantity': 0, 'value': 0.0} for ticker in transactions_dict.keys()}

for ticker, transactions in transactions_dict.items():
    for transaction in transactions:
        date = transaction['date']
        amount = transaction['amount']

        # Fetch the data for the date of the transaction
        data = yf.download(ticker, start=date, end=date, progress=False)
        if data.empty:
            print(f"No data for {ticker} on {date}")
            continue

        # Calculate the quantity bought or sold
        quantity = amount / data['Close'][0]
        portfolio_dict[ticker]['quantity'] += quantity

        # The value is updated later with the current price


