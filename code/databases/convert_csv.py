import csv
import pickle
from pathlib import Path
from datetime import datetime

def convert_csv_to_dict(csv_file_path):
    keys = ['USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON', 'SEK', 'CHF', 'ISK', 'NOK', 'TRY',
            'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB']

    result_dict = {}

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip the header
        for row in csv_reader:
            # Convert date to 'YYYY-MM-DD' format
            date = datetime.strptime(row[0], '%d %B %Y').strftime('%Y-%m-%d')
            values = row[1:]
            currency_data = {keys[i]: float(values[i]) for i in range(len(keys)) if values[i] != 'N/A'}
            result_dict[date] = currency_data

    return result_dict

# Get the current script's directory
SCRIPT_DIR = Path(__file__).parent.resolve()

# Paths to the files
pickle_file_path = SCRIPT_DIR / 'ecb_daily.pkl'
csv_file_path = SCRIPT_DIR / 'eurofxref.csv'

# Load existing data
try:
    with open(pickle_file_path, 'rb') as file:
        existing_data = pickle.load(file)
except FileNotFoundError:
    existing_data = {}  # If the file doesn't exist, start with an empty dictionary

# Convert new CSV data to a dictionary
new_data = convert_csv_to_dict(csv_file_path)
print(new_data.keys())

# Update existing data with new data
existing_data.update(new_data)

# Save the updated data back to the .pkl file
with open(pickle_file_path, 'wb') as file:
    pickle.dump(existing_data, file)
