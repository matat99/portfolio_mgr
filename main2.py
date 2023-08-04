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




def get_weekly_performance(tickers_dict):
    performance_dict = {}
    today = pd.Timestamp.now(tz='UTC').floor('D') - pd.DateOffset(days=1)
    one_week_ago = today - pd.DateOffset(weeks=1)
    today_str = today.strftime('%Y-%m-%d')
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    for name, ticker in tickers_dict.items():
        try:
            data = yf.download(ticker, start=one_week_ago_str, end=today_str, progress=False)
            
            if data.empty:
                performance_dict[name] = 'No data'
                continue

            close_price = data['Close'][-1]
            close_date = data.index[-1]

            week_ago_price = data['Close'][0]
            week_ago_date = data.index[0]

            percentage_change = ((close_price - week_ago_price) / week_ago_price) * 100
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
    position_worth_dict = {}

    for name, ticker in tickers_dict.items():
        try:
            transactions = transactions_dict.get(ticker, [])
            data = yf.download(ticker, progress=False)
            total_worth = 0.0

            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                transaction_amount = transaction['amount']

                transaction_price = data.loc[transaction_date, 'Close']
                shares_bought = transaction_amount / transaction_price

                close_price = data['Close'][-1]
                worth = shares_bought * close_price
                total_worth += worth

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


