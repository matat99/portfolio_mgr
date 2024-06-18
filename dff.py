def convert_dividend_to_gbp(amount, currency, date, fx_rates):
    if currency == 'GBP':
        return amount

    to_eur_rate = fx_rates.get(currency, 1)
    amount_in_eur = amount / to_eur_rate
    eur_to_gbp_rate = fx_rates.get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate


def convert_dividend_to_gbp(amount, currency, date, exchange_rates):
    if currency == 'GBP':
        return amount

    to_eur_rate = exchange_rates[date.strftime("%Y-%m-%d")].get(currency, 1)
    amount_in_eur = amount / to_eur_rate
    eur_to_gbp_rate = exchange_rates[date.strftime("%Y-%m-%d")].get('GBP', 1)
    return amount_in_eur * eur_to_gbp_rate
