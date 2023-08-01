import yfinance as yf
import pandas as pd
import json
from datetime import date,timedelta

# Load tickers from JSON file
with open('tickers.json', 'r') as file:
    tickers_dict = json.load(file)

# Load purchase dates from JSON file
with open('purchase_date.json', 'r') as file:
    purchase_date_dict = json.load(file)

# Load investments from JSON file
with open('investment.json', 'r') as file:
    investment_dict = json.load(file)
