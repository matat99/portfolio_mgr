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

# Convert the investment values to floats
investment_dict = {ticker: float(investment) for ticker, investment in investment_dict.items()}

# Calculate total investment
total_investment = sum(investment_dict.values())

# Calculate weights of each ticker based on the investment
weights_dict = {ticker: investment/total_investment for ticker, investment in investment_dict.items()}

# Fetch data
data = yf.download(tickers_list,'2017-12-18')

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

# Calculate individual stock performance and save to CSV
for ticker in tickers_list:
    # Fetch data for the individual stock
    stock_data = yf.download(ticker,'2017-1-1')

    # Calculate Returns
    stock_returns = stock_data.pct_change()

    # Calculate Cumulative Returns
    stock_cumulative_returns = (1 + stock_returns).cumprod()

    # Create a DataFrame for individual stock performance
    stock_df = pd.DataFrame({
        'Stock Price': stock_data,
        'Dividends': '',  # Placeholder column for manual input
        'Stock Price + Div': '',  # Placeholder column for manual input
        'Weekly % Change': stock_returns.resample('W').apply(lambda x: (x[-1] / x[0]) - 1),
        'Total % Change': stock_cumulative_returns
    })

    # Save to CSV
    stock_df.to_csv(f'{ticker}_performance.csv')
