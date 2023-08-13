# performance_comparison.py

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def get_historical_data(tickers_dict, comparison_start_date, comparison_end_date):
    data_dict = {}
    for name, ticker in tickers_dict.items():
        try:
            # Fetch weekly data using the '1wk' interval
            data = yf.download(ticker, start=comparison_start_date, end=comparison_end_date, interval='1wk', progress=False)['Close']
            data_dict[name] = data
        except Exception as e:
            print(f"Error fetching data for {name}: {e}")
    return data_dict

def get_portfolio_value(data_dict, transactions_dict):
    portfolio_value = pd.Series(dtype=float)
    
    for name, data in data_dict.items():
        try:
            transactions = transactions_dict.get(name, [])
            total_shares = sum([transaction['amount'] / data.loc[transaction['date']] for transaction in transactions])
            weekly_value = data * total_shares
            if portfolio_value.empty:
                portfolio_value = weekly_value
            else:
                portfolio_value = portfolio_value.add(weekly_value, fill_value=0)
        except Exception as e:
            print(f"Error calculating value for {name}: {e}")
    return portfolio_value

def plot_portfolio_vs_benchmark(portfolio_data, benchmark_data, benchmark_name):
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_data.index, portfolio_data, label='Portfolio', color='blue')
    plt.plot(benchmark_data.index, benchmark_data, label=benchmark_name, color='red')
    plt.title('Portfolio Value vs Benchmark Value')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('portfolio_vs_benchmark.png')
    plt.show()

def compare_portfolio_to_benchmark(tickers_dict, transactions_dict, comparison_start_date, comparison_end_date, benchmark_ticker, benchmark_name):
    # Fetch portfolio data over time
    data_dict = get_historical_data(tickers_dict, comparison_start_date, comparison_end_date)
    
    # Calculate portfolio value over time
    portfolio_value = get_portfolio_value(data_dict, transactions_dict)
    
    # Fetch benchmark data
    benchmark_data = yf.download(benchmark_ticker, start=comparison_start_date, end=comparison_end_date, interval='1wk', progress=False)['Close']
    
    # Plot portfolio value against benchmark value
    plot_portfolio_vs_benchmark(portfolio_value, benchmark_data, benchmark_name)
