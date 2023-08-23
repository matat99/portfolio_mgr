import pandas as pd
import yfinance as yf

def calculate_portfolio_value(stocks, start_date, end_date):
    portfolio_value = []
    dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI') # Weekly data on Fridays
    month_first_dates = pd.date_range(start=start_date, end=end_date, freq='MS') # First day of every month
    
    # Initializing the portfolio value dataframe
    portfolio_df = pd.DataFrame({
        'Date': dates,
        'Portfolio Value': [0.0]*len(dates)
    })

    for date in month_first_dates:
        try:
            total_value_for_date = 0
            for stock, quantity in stocks.items():
                stock_data = yf.download(stock, start=date, end=date + pd.Timedelta(days=1))
                if not stock_data.empty:
                    stock_price = stock_data.iloc[0]['Open'] # Assuming you want the 'Open' price. Change if needed.
                    total_value_for_date += stock_price * quantity
                else:
                    raise ValueError(f"No data available for {stock} on {date}")
            # Update the portfolio_df with the calculated value for the date
            portfolio_df.loc[portfolio_df['Date'] == date, 'Portfolio Value'] = total_value_for_date
        except Exception as e:
            print(f"Error processing {stock} at {date}: {e}")

    return portfolio_df

stocks = {
    'AAPL': 10,
    'MSFT': 5,
    'GOOGL': 3
}  # example stocks dictionary

df = calculate_portfolio_value(stocks, '2022-01-01', '2022-12-31')
print(df)
