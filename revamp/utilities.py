# utilities.py

import os
import json
import sys

def load_dict_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

import pandas as pd

def save_to_csv(data, name_to_ticker_map, filename='portfolio_values.csv'):
    # Convert your data from tickers to names
    data_with_names = {name: data[ticker] for name, ticker in name_to_ticker_map.items() if ticker in data}

    # Cash Position (Maybe add a more dynamic manipulation of this value but whatever)
    data_with_names['Cash'] = 499.04

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data_with_names.items(), columns=['Company Name', 'Value'])
    df.to_csv(filename, index=False)


def append_dict_to_txt(dict_obj, filename, sort_by_value=True, reverse=True):
    if sort_by_value:
        dict_obj = dict(sorted(dict_obj.items(), key=lambda item: item[1] if isinstance(item[1], float) else float('-inf'), reverse=reverse))
    with open(filename, 'a') as file:
        for key, value in dict_obj.items():
            file.write(f"{key}: {value}%\n")

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
