# main.py

from datetime import datetime
import os
import pickle
from datetime import timedelta
import pandas as pd

from utilities import load_dict_from_json, save_to_csv
from data_retrieval import weekly_performance, calculate_overall_performance, get_eur_exchange_rates, calculate_position_values_with_currency_adjustment, yearly_performance_June2June, yearly_performance_YoY, weekly_portfolio_performance_with_currency_adjustment, calculate_adjusted_portfolio_values_as_of_date
from data_download import download_data_for_tickers, load_saved_data, download_exchange_rates, load_saved_exchange_rates

api_key = "42c83d3d0b0e24c532ce1cd511d95724" # They key is hard-coded... I know it's bad practice FUCK YOU 

if __name__ == "__main__":

    # Load Transactions and current tickers

    transaction_data = load_dict_from_json('../transactions.json')

    current_tickers = load_dict_from_json('../current_tickers.json')
    
    print(type(transaction_data))

    # Download all the data for tickers and exchange rates

    downloaded_fx = load_saved_exchange_rates()
    #downloaded_fx = download_exchange_rates(api_key)
    #downloaded_data = download_data_for_tickers(transaction_data)
    downloaded_data = load_saved_data() # uses data downloaded onto the computer so not hit the api everytime when debugging
    #eur_rates = get_eur_exchange_rates(api_key)

    # Value of our current positions 
    # Cash position is currently hard-coded in the save_to_csv function (Not long term hopefully)

    #rates = get_eur_exchange_rates(api_key, "2023-01-01")

    
    #value = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data)

    #save_to_csv(value)

    #weekly = weekly_performance(transaction_data, downloaded_data, current_tickers)

    #yearly = yearly_performance_YoY(transaction_data, downloaded_data, current_tickers)

    #overall = calculate_overall_performance(transaction_data, downloaded_data, current_tickers, value['Total Portfolio'])

    #J2J = yearly_performance_June2June(transaction_data, downloaded_data, current_tickers)

    #close = get_close_prices_on_cutoff(downloaded_data, current_tickers)

    #summary = get_portfolio_summary(transaction_data, current_tickers, downloaded_data, eur_rates)

    #graph = monthly_portfolio_performance(transaction_data, downloaded_data, current_tickers)

    #weekly_value = weekly_portfolio_performance_with_currency_adjustment(transaction_data, downloaded_fx, downloaded_data)

    #dated = calculate_adjusted_portfolio_values_as_of_date(transaction_data, downloaded_data, downloaded_fx, date="2022-06-01")


    cutoff_date="2023-05-31"

    def generate_weekly_portfolio_values(transactions_dict, downloaded_data, eur_rates, cutoff_date):
        # Find the first transaction date in the portfolio
        first_transaction_date = min(pd.to_datetime(transaction['date']) for ticker, transactions in transactions_dict.items() for transaction in transactions)
    
        # Initialize an empty dictionary to hold the results
        weekly_portfolio_values = {}
    
        # Generate dates in weekly increments from the first_transaction_date to the cutoff_date
        current_date = first_transaction_date
        cutoff_date = pd.to_datetime(cutoff_date)
    
        while current_date <= cutoff_date:
            # Call the function to calculate the portfolio value for the current date
            position_values = calculate_adjusted_portfolio_values_as_of_date(transactions_dict, downloaded_data, eur_rates, current_date)
        
            # Store the result in the dictionary
            weekly_portfolio_values[current_date] = position_values
        
            # Increment the current date by 7 days
            current_date += timedelta(days=7)
    
        return weekly_portfolio_values

# Assuming transactions_dict, downloaded_data, and eur_rates are available
# cutoff_date = "2023-08-24"
# results = generate_weekly_portfolio_values(transactions_dict, downloaded_data, eur_rates, cutoff_date)
# print(results)

    weekly_l = generate_weekly_portfolio_values(transaction_data, downloaded_data, downloaded_fx, cutoff_date)

    print(weekly_l)
    
    
