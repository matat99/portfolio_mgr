# performance_comparison.py

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def get_historical_data(tickers_dict, comparison_start_date, comparison_end_date):
    data_dict = {}
    for name, ticker in tickers_dict.items():
        try:
            data = yf.download(ticker, start=comparison_start_date, end=comparison_end_date, progress=False)
            data_dict[name] = data['Close']
        except Exception as e:
            print(f"Error fetching data for {name}: {e}")
    return data_dict

def calculate_cumulative_returns(data):
    return (data.pct_change() + 1).cumprod()

def plot_performance_against_benchmark(portfolio_data, benchmark_data, benchmark_name):
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_data.index, portfolio_data, label='Portfolio', color='blue')
    plt.plot(benchmark_data.index, benchmark_data, label=benchmark_name, color='red')
    plt.title('Portfolio Performance vs Benchmark')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('performance_vs_benchmark.png')
    plt.show()

def compare_portfolio_to_benchmark(tickers_dict, comparison_start_date, comparison_end_date, benchmark_ticker, benchmark_name):
    # Fetch historical data for portfolio
    portfolio_data = get_historical_data(tickers_dict, comparison_start_date, comparison_end_date)
    
    # Calculate portfolio cumulative returns
    portfolio_cumulative_returns = calculate_cumulative_returns(pd.concat(portfolio_data, axis=1).sum(axis=1))
    
    # Fetch benchmark data
    benchmark_data = yf.download(benchmark_ticker, start=comparison_start_date, end=comparison_end_date, progress=False)['Close']
    
    # Calculate benchmark cumulative returns
    benchmark_cumulative_returns = calculate_cumulative_returns(benchmark_data)
    
    # Plot performance against benchmark
    plot_performance_against_benchmark(portfolio_cumulative_returns, benchmark_cumulative_returns, benchmark_name)
