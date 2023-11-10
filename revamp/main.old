# main.py

from datetime import datetime
import os
import pickle
from datetime import timedelta
import pandas as pd
import csv

from utilities import load_dict_from_json, save_to_csv
from data_retrieval import weekly_performance, calculate_overall_performance, get_eur_exchange_rates, calculate_position_values_with_currency_adjustment, yearly_performance_June2June, yearly_performance_YoY, weekly_portfolio_performance_with_currency_adjustment, calculate_total_portfolio_value_as_of_date, weekly_portfolio_values
from data_download import download_data_for_tickers, load_saved_data, download_weekly_exchange_rates, load_saved_exchange_rates

api_key = "42c83d3d0b0e24c532ce1cd511d95724" # They key is hard-coded... I know it's bad practice FUCK YOU 

if __name__ == "__main__":

    # Load Transactions and current tickers

    transaction_data = load_dict_from_json('../transactions.json')

    current_tickers = load_dict_from_json('../current_tickers.json')
    
    #print(type(transaction_data))

    # Download all the data for tickers and exchange rates

    #downloaded_fx = load_saved_exchange_rates()
    downloaded_fx = download_weekly_exchange_rates(api_key)
    #downloaded_data = download_data_for_tickers(transaction_data)
    downloaded_data = load_saved_data() # uses data downloaded onto the computer so not hit the api everytime when debugging
    #eur_rates = get_eur_exchange_rates(api_key)

    # Value of our current positions 
    # Cash position is currently hard-coded in the save_to_csv function (Not long term hopefully)

    #rates = get_eur_exchange_rates(api_key, "2023-01-01")

    
    #value = calculate_position_values_with_currency_adjustment(transaction_data, current_tickers, downloaded_data)

    #save_to_csv(value)

    weekly_something = weekly_portfolio_values(transaction_data, downloaded_data, api_key)

    #weekly = weekly_performance(transaction_data, downloaded_data, current_tickers)

    #yearly = yearly_performance_YoY(transaction_data, downloaded_data, current_tickers)

    #overall = calculate_overall_performance(transaction_data, downloaded_data, current_tickers, value['Total Portfolio'])

    #J2J = yearly_performance_June2June(transaction_data, downloaded_data, current_tickers)

    #close = get_close_prices_on_cutoff(downloaded_data, current_tickers)

    #summary = get_portfolio_summary(transaction_data, current_tickers, downloaded_data, eur_rates)

    #graph = monthly_portfolio_performance(transaction_data, downloaded_data, current_tickers)

    #weekly_value = weekly_portfolio_performance_with_currency_adjustment(transaction_data, downloaded_fx, downloaded_data)

    #dated = calculate_adjusted_portfolio_values_as_of_date(transaction_data, downloaded_data, downloaded_fx, date="2022-06-01")

    #cutoff_date = "2023-05-31"

    #print(downloaded_data)

    #weekly_value = calculate_total_portfolio_value_as_of_date(transaction_data, downloaded_data, downloaded_fx, date="2022-05-31")

    print(weekly_something)
    #print(value)


    # # Your function to generate weekly dates
    # def generate_weekly_dates(cutoff_date, end_date="2023-05-31"):
    #     weekly_dates = []
        
    #     # Convert the dates to datetime objects for manipulation
    #     cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d")
    #     end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
    #     # Generate weekly dates from end_date backwards to cutoff_date
    #     current_date = end_date
    #     while current_date >= cutoff_date:
    #         weekly_dates.append(current_date.strftime("%Y-%m-%d"))
    #         current_date -= timedelta(days=7)
        
    #     return weekly_dates

    # # Generate weekly dates from 2022-05-17 to 2023-05-31
    # weekly_dates = generate_weekly_dates("2017-12-18")

    # # Dictionary to hold the total portfolio value for each date
    # total_portfolio_values = {}

    # # Loop over each weekly date and calculate the total portfolio value
    # for date in weekly_dates:
    #     total_value = calculate_total_portfolio_value_as_of_date(transaction_data, downloaded_data, downloaded_fx, date=date)
    #     total_portfolio_values[date] = total_value

    # with open('total_portfolio_values.csv', 'w', newline='') as csvfile:
    #     fieldnames = ['Date', 'Total Portfolio Value']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for date, value in total_portfolio_values.items():
    #         writer.writerow({'Date': date, 'Total Portfolio Value': value})

    # print(type(transaction_data))
    # print(downloaded_data['ESGD'].head())
    # print(type(downloaded_data['ESGD'].index[0]))