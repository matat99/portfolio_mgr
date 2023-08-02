import yfinance as yf
import json 
import datetime
import pandas as pd

with open('transactions.json','r') as file:
	transactions_dict = json.load(file)
import pandas as pd

# Set the date to check
check_date = pd.to_datetime("2023-07-25")

# Create an empty dictionary to store the results
check_results = {}

# Fetch the close price for each ticker
for ticker in transactions_dict.keys():
    try:
        # Set a date range around the target date
        start_date = (check_date - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
        end_date = (check_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d')

        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty:
            check_results[ticker] = "No data"
        else:
            # Extract data for the target date
            if check_date in data.index:
                check_results[ticker] = {"price": data.loc[check_date, 'Close'], "date": check_date.strftime('%Y-%m-%d')}
            else:
                check_results[ticker] = "No data on target date"
    except Exception as e:
        check_results[ticker] = f"Error: {e}"

# Print the results
for ticker, result in check_results.items():
    print(f"{ticker}: {result}")

