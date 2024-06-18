import csv
import pickle

def convert_csv_to_dict(csv_file_path):
    # Define the keys in the order they appear in the CSV, excluding 'Date'
    keys = ['USD', 'JPY', 'BGN', 'CYP', 'CZK', 'DKK', 'EEK', 'GBP', 'HUF', 'LTL', 'LVL', 'MTL', 'PLN', 'ROL', 'RON',
            'SEK', 'SIT', 'SKK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRL', 'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD',
            'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB', 'ZAR']

    result_dict = {}

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip the header
        for row in csv_reader:
            date = row[0]
            values = row[1:]
            currency_data = {keys[i]: float(values[i]) for i in range(len(keys)) if values[i] != 'N/A'}
            result_dict[date] = currency_data

    return result_dict

# Example usage
csv_file_path = 'eurofxref-hist.csv'
result = convert_csv_to_dict(csv_file_path)
with open('ecb_daily.pkl', 'wb') as pkl_file:
    pickle.dump(result, pkl_file)
