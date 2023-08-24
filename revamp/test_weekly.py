import pandas as pd
import numpy as np
import yfinance as yf
import pickle  # Don't forget to import this if you're loading exchange rates using pickle.

def fetch_data_for_stocks(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        try:
            stock_data[ticker] = yf.download(ticker, start=start_date, end=end_date)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    return stock_data

def load_saved_exchange_rates(file_name="exchange_rates_data.pkl"):
    with open(file_name, "rb") as f:
        data_dict = pickle.load(f)
    return data_dict

def calculate_portfolio_value(portfolio, start_date, end_date):
    stock_data = fetch_data_for_stocks(portfolio.keys(), start_date, end_date)
    exchange_rates = load_saved_exchange_rates()

    # Map tickers to their respective currency
    currency_mapping = {
        'AAPL': 'USD',
        'GOOGL': 'USD',
        'MSFT': 'USD'
        # ... Add other tickers and their currency if necessary
    }

    dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')
    df = pd.DataFrame(index=dates)

    df['Portfolio Value'] = 0.0
    for date in dates:
        for ticker, quantity in portfolio.items():
            try:
                closing_price = stock_data[ticker].loc[date, 'Close']
            except KeyError:
                available_dates = stock_data[ticker].index
                previous_dates = available_dates[available_dates < date]
                if previous_dates.empty:
                    print(f"No available previous data for {ticker} on {date}")
                    continue
                last_available_date = previous_dates[-1]
                closing_price = stock_data[ticker].loc[last_available_date, 'Close']
            
            # Currency conversion using EUR as a pivot
            currency = currency_mapping[ticker]
            month_start = date.replace(day=1)  # Get the start of the month to match your exchange rate data
            current_rates = exchange_rates.get(month_start)

            if currency != 'EUR' and current_rates:
                to_eur_rate = 1 / current_rates[currency] if currency in current_rates else 1
                value_in_eur = quantity * closing_price * to_eur_rate
                # Convert to GBP
                value_in_gbp = value_in_eur * current_rates['GBP']
            else:
                value_in_gbp = quantity * closing_price

            df.loc[date, 'Portfolio Value'] += value_in_gbp

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    return df

portfolio = {
    'AAPL': 10,
    'GOOGL': 5,
    'MSFT': 15
}

start_date = '2020-01-01'
end_date = '2021-01-01'

df = calculate_portfolio_value(portfolio, start_date, end_date)
print(df)
