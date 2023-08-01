import yfinance as yf
import pandas as pd
import json

# Load tickers from JSON file
with open('tickers.json', 'r') as file:
    tickers_dict = json.load(file)

# Get the list of tickers
tickers_list = list(tickers_dict.values())

# Load investments from JSON file
with open('investment.json', 'r') as file:
    investment_dict = json.load(file)
