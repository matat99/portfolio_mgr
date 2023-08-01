import yfinance as yf

stock_data = yf.download('LLOY.L','2017-12-18')

print(stock_data)