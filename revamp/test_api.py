import requests

API_KEY = "42c83d3d0b0e24c532ce1cd511d95724"

def get_eur_exchange_rates(api_key):
    url = f"http://api.exchangeratesapi.io/latest?base=EUR&access_key={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'rates' not in data:
        raise ValueError(f"API response did not contain 'rates': {data}")

    return {
        'GBP': data['rates']['GBP'],
        'USD': data['rates']['USD']
    }

def test_get_eur_exchange_rates():
    rates = get_eur_exchange_rates(API_KEY)
    
    # Basic check: Ensure the rates for GBP and USD exist in the response and are greater than zero.
    assert 'GBP' in rates and rates['GBP'] > 0, f"Invalid rate for GBP: {rates.get('GBP', 'N/A')}"
    assert 'USD' in rates and rates['USD'] > 0, f"Invalid rate for USD: {rates.get('USD', 'N/A')}"

    print("All tests passed!")

# Run the test function
test_get_eur_exchange_rates()
