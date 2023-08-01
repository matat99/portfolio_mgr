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
