from data_download import fetch_and_save_exchange_rates

api_key = "42c83d3d0b0e24c532ce1cd511d95724"  # Replace with your actual API key
base = "EUR"
file_path = "exchange_rates.pkl"


if __name__ == '__main__':

	stuffz = fetch_and_save_exchange_rates(api_key, base, file_path)
	print('done?')