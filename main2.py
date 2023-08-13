import os
import json
import math
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
from performance_comparison import compare_portfolio_to_benchmark

def load_dict_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def get_weekly_performance(tickers_dict):
    performance_dict = {}
    today = pd.Timestamp.now(tz='UTC').floor('D') - pd.DateOffset(days=1)
    one_week_ago = today - pd.DateOffset(weeks=1)

    for name, ticker in tickers_dict.items():
        try:
            data = yf.download(ticker, start=one_week_ago.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'), progress=False)
            if data.empty:
                performance_dict[name] = 'No data'
                continue

            week_ago_price = data['Close'][0]
            close_price = data['Close'][-1]
            percentage_change = round(((close_price - week_ago_price) / week_ago_price) * 100, 2)
            performance_dict[name] = percentage_change

            print(f"{name} \nWeek Ago Date: {one_week_ago}, Week Ago Price: {week_ago_price}\nClose Date: {today}, Close Price: {close_price}\n")

        except Exception as e:
            performance_dict[name] = f"Error: {e}"
    return performance_dict

def get_position_worth(tickers_dict, transactions_dict):
    position_worth_dict = {}
    for name, ticker in tickers_dict.items():
        try:
            transactions = transactions_dict.get(ticker, [])
            data = yf.download(ticker, progress=False)
            total_worth = 0.0
            for transaction in transactions:
                transaction_date = pd.to_datetime(transaction['date'])
                shares_bought = transaction['amount'] / data.loc[transaction_date, 'Close']
                total_worth += shares_bought * data['Close'][-1]
            position_worth_dict[name] = total_worth
        except Exception as e:
            position_worth_dict[name] = f"Error: {e}"
    return position_worth_dict

def append_dict_to_txt(dict_obj, filename, sort_by_value=True, reverse=True):
    if sort_by_value:
        dict_obj = dict(sorted(dict_obj.items(), key=lambda item: item[1] if isinstance(item[1], float) else float('-inf'), reverse=reverse))
    with open(filename, 'a') as file:
        for key, value in dict_obj.items():
            file.write(f"{key}: {value}%\n")

def plot_portfolio_composition(worth_dict, filename):
    names = list(worth_dict.keys()) 
    worth = list(worth_dict.values())
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(worth, labels=names, autopct='%1.1f%%', pctdistance=1.15, textprops={'fontsize': 10})
    ax.legend(wedges, names,
          title="Portfolio",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title('Portfolio Composition')
    plt.savefig(filename)
    plt.close()


def create_directory():
    date_str = datetime.today().strftime('%Y-%m-%d')
    directory_path = os.path.join(os.getcwd(), date_str)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def redirect_print_to_file(filename):
    original_stdout = sys.stdout
    sys.stdout = open(filename, 'w')
    return original_stdout

def restore_print(original_stdout):
    sys.stdout.close()
    sys.stdout = original_stdout

if __name__ == "__main__":
    import sys

    current_tickers_dict = load_dict_from_json('current_tickers.json')
    transactions_dict = load_dict_from_json('transactions.json')

    output_directory = create_directory()
    output_filename = os.path.join(output_directory, 'overview.txt')
    original_stdout = redirect_print_to_file(output_filename)

    weekly_performance = get_weekly_performance(current_tickers_dict)
    append_dict_to_txt(weekly_performance, output_filename)

    position_worth = get_position_worth(current_tickers_dict, transactions_dict)
    position_worth['Cash'] = 499.04
    for name, worth in position_worth.items():
        print(f"\n{name}: {worth}")

    restore_print(original_stdout)
    
    plot_filename = os.path.join(output_directory, 'portfolio_Composition.png')
    plot_portfolio_composition(position_worth, plot_filename)

    # Compare portfolio performance to FTSE Developed Index
    comparison_start_date = '2022-09-01'
    comparison_end_date = '2023-08-01'
    compare_portfolio_to_benchmark(current_tickers_dict, transactions_dict, comparison_start_date, comparison_end_date, '^FTSE', 'FTSE Developed Index')

            
