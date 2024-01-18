import streamlit as st
import csv
import os

def load_csv_to_dict(file_path):
    data_dicts = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data_dicts.append(row)
    return data_dicts

def main():
    # Assuming the CSV file is named 'data.csv' and is in the current working directory
    csv_file_name = 'darkwave_bands.csv'
    csv_file_path = os.path.join(os.getcwd(), csv_file_name)

    if os.path.exists(csv_file_path):
        data = load_csv_to_dict(csv_file_path)
        # Display the data in Streamlit
        st.write("CSV Data:", data)
    else:
        st.error(f"File {csv_file_name} not found in the working directory.")

if __name__ == "__main__":
    st.title("CSV Loader App")
    main()
