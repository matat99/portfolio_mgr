import json
import yfinance as yf

# Load transactions from JSON file
with open('transactions.json', 'r') as file:
    transactions_dict = json.load(file)

# Create an empty list to store tickers for which no data could be fetched
no_data_tickers = []

# Iterate over tickers
for ticker in transactions_dict.keys():
    try:
        # Fetch the last month of data for the ticker
        data = yf.download(ticker, period="1mo", progress=False)
        
        if data.empty:
            no_data_tickers.append(ticker)
            continue

        # Fetch the last available close price
        close_price = data['Close'][-1]
        print(f"Latest available close price for {ticker}: {close_price}")

    except Exception as e:
        print(f"An error occurred while processing {ticker}: {e}")

# Print the tickers for which no data could be fetched
if no_data_tickers:
    print(f"No data could be fetched for the following tickers: {', '.join(no_data_tickers)}")
