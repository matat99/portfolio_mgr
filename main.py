import yfinance as yf
import pandas as pd
import json

# Load tickers from JSON file
with open('tickers.json', 'r') as file:
    tickers_list = json.load(file)

# Load investments from JSON file
with open('investment.json', 'r') as file:
    investment_dict = json.load(file)

# Calculate total investment
total_investment = sum(investment_dict.values())

# Calculate weights of each ticker based on the investment
weights_dict = {ticker: investment/total_investment for ticker, investment in investment_dict.items()}

# Fetch data
data = yf.download(tickers_list,'2017-1-1')['Adj Close']

# Calculate Returns
returns = data.pct_change()

# Calculate Cumulative Returns
cumulative_returns = (1 + returns).cumprod()

# Calculate total cumulative returns in terms of investment value
portfolio_cumulative_returns = (cumulative_returns * total_investment * pd.Series(weights_dict)).sum(axis=1)

# Create a DataFrame for portfolio cumulative returns
portfolio_cumulative_returns_df = pd.DataFrame(portfolio_cumulative_returns, columns=["Portfolio Value"])

# Save to CSV
portfolio_cumulative_returns_df.to_csv('portfolio_value.csv')

print(portfolio_cumulative_returns_df)
