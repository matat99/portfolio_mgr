# IMPORTANT IMPORTANT for future reference NTT DO COMO: selling it we made 422.27 profit and got 74.35 in dividends


import yfinance as yf
import pandas as pd
import json
from datetime import date,timedelta
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt

# Load tickers from JSON file
with open('current_tickers.json', 'r') as file:
    tickers_dict = json.load(file)

# Load transactions from JSON file
with open('transactions.json', 'r') as file:
    transactions_dict = json.load(file)


# Create an empty portfolio dictionary 
portfolio_dict = {}

# Record Transactions

def get_price_on_date(ticker, date_str):
    """
    Get the closing price of a given stock ticker on a specific date.

    Parameters:
    ticker (str): The ticker symbol of the stock.
    date_str (str): The date to get the price for, in 'YYYY-MM-DD' format.

    Returns:
    float: The closing price on the specified date. 
           Returns 'No data' if no price data is available for the date.
    """
    # Convert date string to datetime
    check_date = pd.to_datetime(date_str)

    # Set a date range around the target date
    start_date = (check_date - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    end_date = (check_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d')

    try:
        # Fetch data for the date range
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # Extract data for the target date
        if check_date in data.index:
            return data.loc[check_date, 'Close']
        else:
            return 'No data'
    except Exception as e:
        return f'Error: {e}'


# Populate the portfolio dictionary
for ticker, transactions in transactions_dict.items():
    # Skip if there are no transactions for the ticker
    if not transactions:
        continue

    # Sort transactions by date
    transactions_sorted = sorted(transactions, key=lambda k: pd.to_datetime(k['date']))

    # Get the first transaction
    first_transaction = transactions_sorted[0]

    # Fetch the price on the date of the first transaction
    price = get_price_on_date(ticker, first_transaction['date'])

    # Add the ticker to the portfolio dictionary with the value, price, and date
    portfolio_dict[ticker] = {
        'value': first_transaction['amount'],
        'price': price,
        'date': first_transaction['date'],
    }


def get_weekly_performance(tickers_dict):
    # Create a dictionary to store the performance for each ticker
    performance_dict = {}

    # Get today's date and one week ago date in the required format
    today = pd.Timestamp.now(tz='UTC').floor('D') - pd.DateOffset(days=1)
    one_week_ago = today - pd.DateOffset(weeks=1)

    # Convert to string format that yf.download understands
    today_str = today.strftime('%Y-%m-%d')
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    # Iterate through each ticker
    for name, ticker in tickers_dict.items():
        try:
            # Get the data for the past week
            data = yf.download(ticker, start=one_week_ago_str, end=today_str, progress=False)
            
            if data.empty:
                performance_dict[name] = 'No data'
                continue

            # Get the last available close price
            close_price = data['Close'][-1]
            close_date = data.index[-1]

            # Get the close price from a week ago
            week_ago_price = data['Close'][0]
            week_ago_date = data.index[0]

            # Calculate the percentage change
            percentage_change = ((close_price - week_ago_price) / week_ago_price) * 100

            # Store the percentage change in the performance dictionary
            performance_dict[name] = round(percentage_change, 2)

            print(f"{name} \nWeek Ago Date: {week_ago_date}, Week Ago Price: {week_ago_price}\nClose Date: {close_date}, Close Price: {close_price}\n")

        except Exception as e:
            performance_dict[name] = f"Error: {e}"

    return performance_dict

# Load the current tickers from the JSON file
with open('current_tickers.json', 'r') as file:
    current_tickers_dict = json.load(file)

# Get the weekly performance
weekly_performance = get_weekly_performance(current_tickers_dict)

# Sort the performance dictionary by performance
sorted_weekly_performance = dict(sorted(weekly_performance.items(), key=lambda item: item[1] if isinstance(item[1], float) else -math.inf, reverse=True))

with open('weekly_performance.txt','w') as file:
    for ticker, performance in sorted_weekly_performance.items():
        file.write(f"{ticker}: {performance}%\n")
# Print the results
# print(f"Full performance: {sorted_weekly_performance}")


def get_position_worth(tickers_dict, transactions_dict):
    # Create a dictionary to store the worth of each position
    position_worth_dict = {}

    # Iterate through each ticker
    for name, ticker in tickers_dict.items():
        try:
            # Get the transactions for the current ticker
            transactions = transactions_dict.get(ticker, [])

            # Get the historical data for the current ticker
            data = yf.download(ticker, progress=False)

            # Initialize a variable to store the total worth of the position
            total_worth = 0.0

            # Iterate through each transaction
            for transaction in transactions:
                # Get the date and amount of the transaction
                transaction_date = pd.to_datetime(transaction['date'])
                transaction_amount = transaction['amount']

                # Get the close price on the date of the transaction
                transaction_price = data.loc[transaction_date, 'Close']

                # Calculate the number of shares bought
                shares_bought = transaction_amount / transaction_price

                # Get the last available close price
                close_price = data['Close'][-1]

                # Calculate the current worth of the shares bought in the transaction
                worth = shares_bought * close_price

                # Add the worth of the current transaction to the total worth
                total_worth += worth

            # Store the total worth in the position worth dictionary
            position_worth_dict[name] = total_worth

        except Exception as e:
            position_worth_dict[name] = f"Error: {e}"

    return position_worth_dict

# Load the current tickers from the JSON file
with open('current_tickers.json', 'r') as file:
    current_tickers_dict = json.load(file)

# Load the transactions from the JSON file
with open('transactions.json', 'r') as file:
    transactions_dict = json.load(file)

# Get the worth of each position
position_worth = get_position_worth(current_tickers_dict, transactions_dict)

# Print the results
for name, worth in position_worth.items():
    print(f"{name}: {worth}")


# Add the cash position to the position worth dictionary
position_worth['Cash'] = 499.04

# Get the names of the positions and their worth
names = list(position_worth.keys())
worth = list(position_worth.values())

# Create a pie chart
fig, ax = plt.subplots()
ax.pie(worth, labels=names, autopct='%1.1f%%')

# Add a title
ax.set_title('Portfolio Composition')

plt.savefig('portfolio_Composition.png')

# Show the plot
plt.show()


