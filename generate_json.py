import csv
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# Geocoding function using geopy
def add_lat_long(data_dicts):
    geolocator = Nominatim(user_agent="darkwaveproject123$")

    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for entry in data_dicts:
        city = entry['city']
        state = entry['state']
        country = entry['country']  # Replace with actual key names if different
        if city == "None":
            city = None
        if city and state and country:
            location = geocode(f"{city}, {state}, {country}")
        elif city and country:
            location = geocode(f"{city}, {country}")
        elif country:
            location = geocode(f"{country}")
        if location:
            entry['latitude'] = location.latitude
            entry['longitude'] = location.longitude
        else:
            entry['latitude'] = None
            entry['longitude'] = None
    return data_dicts

# Function to load CSV data
def load_csv_to_dict(file_path):
    data_dicts = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data_dicts.append(row)
    return data_dicts

# Function to save data as JSON
def save_data_to_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Main execution
def main():
    csv_file_name = 'darkwave_bands.csv'  # Replace with your CSV file name
    csv_file_path = os.path.join(os.getcwd(), csv_file_name)
    json_file_name = 'darkwave_bands.json'  # Output JSON file name

    if os.path.exists(csv_file_path):
        data_dicts = load_csv_to_dict(csv_file_path)
        updated_data = add_lat_long(data_dicts)
        save_data_to_json(updated_data, json_file_name)
        print(f"Data has been processed and saved to {json_file_name}")
    else:
        print(f"File {csv_file_name} not found in the working directory.")

if __name__ == "__main__":
    main()
