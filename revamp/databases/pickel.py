import pickle

with open('downloaded_data.pkl', 'rb') as file:
    data = pickle.load(file)

# Now you can inspect the data
print(data)
