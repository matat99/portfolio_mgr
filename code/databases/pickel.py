import pickle

with open('ecb_daily.pkl', 'rb') as file:
    data = pickle.load(file)

# Now you can inspect the data
print(data)
