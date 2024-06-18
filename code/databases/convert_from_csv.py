import csv
import pickle

# Function to convert CSV data to a dictionary
def convert_csv_to_dict(csv_file_path):
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

# Load existing data
try:
    with open('ecb_daily.pkl', 'rb') as file:
        existing_data = pickle.load(file)
except FileNotFoundError:
    existing_data = {}  # If the file doesn't exist, start with an empty dictionary

# Convert new CSV data to a dictionary
csv_file_path = 'path_to_your_csv_file.csv'  # Replace with your actual CSV file path
new_data = convert_csv_to_dict(csv_file_path)

# Update existing data with new data
existing_data.update(new_data)

# Save the updated data back to the .pkl file
with open('ecb_daily.pkl', 'wb') as file:
    pickle.dump(existing_data, file)
