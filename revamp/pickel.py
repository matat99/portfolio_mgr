import pickle

with open('./databases/exchange_rates.pkl', 'rb') as file:
    data = pickle.load(file)

# Now you can inspect the data
print(data)
