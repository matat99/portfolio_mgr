import pandas as pd
import xlsxwriter
from utilities import load_dict_from_json  # Assuming this has the required functions

def main():
    # Load Transactions and current tickers
    transaction_data = load_dict_from_json('../transactions.json')
    current_tickers = load_dict_from_json('../current_tickers.json')

    # Load downloaded data and exchange rates (adjust paths as needed)
    with open('./datalsbases/downloaded_data.pkl', 'rb') as f:
        downloaded_data = pickle.load(f)

    with open('./databases/exchange_rates.pkl', 'rb') as f:
        downloaded_fx = pickle.load(f)

    # Preprocess and combine stock data
    stock_data_combined = pd.DataFrame(index=downloaded_fx.index)
    for ticker, data in downloaded_data.items():
        stock_data_combined[f'{ticker} - Close'] = data['Close']
        stock_data_combined[f'{ticker} - Dividends'] = data['Dividends'].fillna(0)

    # Filter exchange rate data
    fx_data_filtered = downloaded_fx[['USD', 'GBP', 'CAD']]

    # Combine stock data with filtered exchange rate data
    historical_data = pd.concat([stock_data_combined, fx_data_filtered], axis=1)

    # Define the path for the Excel file
    excel_file_path = 'historical_data.xlsx'

    # Create a Pandas Excel writer using xlsxwriter as the engine
    writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
    historical_data.to_excel(writer, sheet_name='historical data')

    # Close the Pandas Excel writer and output the Excel file
    writer.close()

    print("Historical data report generated and saved to 'historical_data.xlsx'")

if __name__ == "__main__":
    main()
