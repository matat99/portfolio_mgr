# main.py

from datetime import datetime
import os

from utilities import load_dict_from_json, save_to_csv
from data_retrieval import weekly_performance, calculate_overall_performance, get_eur_exchange_rates, calculate_position_values_with_currency_adjustment, yearly_performance_June2June, yearly_performance_YoY, monthly_portfolio_performance, get_close_prices_on_cutoff, get_portfolio_summary
from data_download import download_data_for_tickers, load_saved_data

api_key = "42c83d3d0b0e24c532ce1cd511d95724" # They key is hard-coded... I know it's bad practice FUCK YOU 

if __name__ == "__main__":

    # Load Transactions and current tickers

    transaction_data = load_dict_from_json('../transactions.json')

    current_tickers = load_dict_from_json('../current_tickers.json')
    
    print(type(transaction_data))

    # Download all the data for tickers and exchange rates

    #downloaded_data = download_data_for_tickers(transaction_data)
    downloaded_data = load_saved_data() # uses data downloaded onto the computer so not hit the api everytime when debugging
    eur_rates = get_eur_exchange_rates(api_key)

    # Value of our current positions 
    # Cash position is currently hard-coded in the save_to_csv function (Not long term hopefully)

    
    value = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data, eur_rates)

    save_to_csv(value)

    #weekly = weekly_performance(transaction_data, downloaded_data, current_tickers)

    #yearly = yearly_performance_YoY(transaction_data, downloaded_data, current_tickers)

    overall = calculate_overall_performance(transaction_data, downloaded_data, current_tickers, value['Total Portfolio'])

    J2J = yearly_performance_June2June(transaction_data, downloaded_data, current_tickers)

    #close = get_close_prices_on_cutoff(downloaded_data, current_tickers)

    #summary = get_portfolio_summary(transaction_data, current_tickers, downloaded_data, eur_rates)

    #graph = monthly_portfolio_performance(transaction_data, downloaded_data, current_tickers)

    print(J2J)
    
