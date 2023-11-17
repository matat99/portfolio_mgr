import unittest
import pandas as pd
import json
from data_retrieval import calculate_position_values_with_currency_adjustment
from data_download import (
    load_saved_data,
    load_saved_exchange_rates
)

class TestCalculatePositionValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load transactions from JSON file
        with open('../transactions.json', 'r') as file:
            cls.transactions_dict = json.load(file)

        # Load current tickers from JSON file
        with open('../current_tickers.json', 'r') as file:
            cls.current_tickers = json.load(file)

        # Load saved exchange rates and ticker data
        cls.downloaded_fx = load_saved_exchange_rates()
        cls.downloaded_data = load_saved_data()

    def test_calculate_position_values(self):
        # Call the function with the loaded data
        position_values_df, total_portfolio_value = calculate_position_values_with_currency_adjustment(
            self.transactions_dict, self.current_tickers, self.downloaded_data, self.downloaded_fx)

        # Print the position values and total portfolio value
        print(position_values_df)
        print(f'Total Portfolio Value (GBP): {total_portfolio_value}')

# Run the tests
if __name__ == '__main__':
    unittest.main()
