import pickle
import os

# Path to the pickle file
pickle_file = "./eve_wiggin/eve_wiggin/data/ama_min.pickle"

# Load the pickle file
with open(pickle_file, "rb") as f:
    systems_data = pickle.load(f)

# Print the type of systems_data
print(f"Type of systems_data: {type(systems_data)}")

# Print the length of systems_data if it's a collection
if hasattr(systems_data, "__len__"):
    print(f"Length of systems_data: {len(systems_data)}")

# Print the first few items to understand the structure
if isinstance(systems_data, list):
    for i, item in enumerate(systems_data[:5]):
        print(f"Item {i} type: {type(item)}")
        print(f"Item {i} content: {item}")
elif isinstance(systems_data, dict):
    for i, (key, value) in enumerate(list(systems_data.items())[:5]):
        print(f"Key {i}: {key}, Value type: {type(value)}")
        print(f"Value {i} content: {value}")
else:
    print(f"Content: {systems_data}")

