import json
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

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

            performance_dict[name] = round(((close_price - week_ago_price) / week_ago_price) * 100, 2)
            print(f"{name} \nWeek Ago Date: {data.index[0]}, Week Ago Price: {week_ago_price}\nClose Date: {data.index[-1]}, Close Price: {close_price}\n")
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

def save_sorted_performance_to_txt(sorted_dict, filename):
    with open(filename,'w') as file:
        for ticker, performance in sorted_dict.items():
            file.write(f"{ticker}: {performance}%\n")

def plot_portfolio_composition(worth_dict):
    names = list(worth_dict.keys())
    worth = list(worth_dict.values())
    fig, ax = plt.subplots()
    ax.pie(worth, labels=names, autopct='%1.1f%%')
    ax.set_title('Portfolio Composition')
    plt.savefig('portfolio_Composition.png')
    plt.show()

if __name__ == "__main__":
    current_tickers_dict = load_dict_from_json('current_tickers.json')
    transactions_dict = load_dict_from_json('transactions.json')

    weekly_performance = get_weekly_performance(current_tickers_dict)
    sorted_weekly_performance = dict(sorted(weekly_performance.items(), key=lambda item: item[1] if isinstance(item[1], float) else float('-inf'), reverse=True))

    save_sorted_performance_to_txt(sorted_weekly_performance, 'weekly_performance.txt')

    position_worth = get_position_worth(current_tickers_dict, transactions_dict)
    position_worth['Cash'] = 499.04

    for name, worth in position_worth.items():
        print(f"{name}: {worth}")

    print(f'{sorted_weekly_performance}')

    plot_portfolio_composition(position_worth)
