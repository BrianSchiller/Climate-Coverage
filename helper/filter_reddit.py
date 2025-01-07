import json
from datetime import datetime

# Load the JSON file
path = "reddit/climateactionplan.json"
with open(path, 'r') as file:
    data = json.load(file)

# Define the date range for filtering
start_date = datetime.strptime("2024-10-28", "%Y-%m-%d")
end_date = datetime.strptime("2024-12-29", "%Y-%m-%d")

# Filter the entries based on the "Created" field
filtered_data = [
    entry for entry in data
    if start_date <= datetime.strptime(entry['Created'], "%Y-%m-%d %H:%M:%S") <= end_date
]

# Save the filtered data back to a JSON file
with open(path, 'w') as file:
    json.dump(filtered_data, file, indent=4)

print(f"Filtered data saved to 'filtered_data.json'. Total entries: {len(filtered_data)}")