from data_download import load_saved_exchange_rates
import datetime 

def get_exchange_rates(data, start_date, end_date):
    # Convert string dates to datetime objects for comparison
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    # Filter the data dictionary based on the date range and extract rates
    filtered_data = {k: v for k, v in data.items() if start_date <= datetime.datetime.strptime(k, "%Y-%m-%d").date() <= end_date}
    
    gbp_rates = {k: v['GBP'] for k, v in filtered_data.items()}
    usd_rates = {k: v['USD'] for k, v in filtered_data.items()}
    cad_rates = {k: v['CAD'] for k, v in filtered_data.items()}
    
    return {
        "GBP": gbp_rates,
        "USD": usd_rates,
        "CAD": cad_rates
    }

# Example usage

downloaded_data = load_saved_exchange_rates()

get_exchange_rates(downloaded_data, "2021-01-01", "2023-05-01")
