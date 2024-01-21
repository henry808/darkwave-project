import streamlit as st
import json
import os
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
# import plotly.express as px
from datetime import datetime

def stack_labels(df, key='band', offset=0.015):
    # Group by the position and stack labels
    grouped = df.groupby(['latitude', 'longitude'])
    for (lat, lon), group in grouped:
        for i, (_, row) in enumerate(group.iterrows()):
            df.loc[row.name, 'stacked_latitude'] = lat + i * offset
    return df

def load_json_to_dict(file_path):
    with open(file_path, 'r') as file:
        data_dicts = json.load(file)
    return data_dicts

def display_location_map(data):
    df = pd.DataFrame(data)
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Update DataFrame with jittered coordinates
    df = stack_labels(df)

    # Tooltip for the ScatterplotLayer
    tooltip = {
        "html": "<b>{band}</b>",
        "style": {
            "backgroundColor": "steelblue",
            "color": "black"
        }
    }

    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=1
    )

    # ScatterplotLayer for the points
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position=["longitude", "stacked_latitude"],
        get_color=[0, 255, 0, 255],  # RGB color format
    )

    # TextLayer to display band names
    text_layer = pdk.Layer(
        "TextLayer",
        df,
        pickable=False,
        get_position=["longitude", "stacked_latitude"],
        get_text="band",  # Assuming 'band' is the key for band names in your data
        get_size=16,
        get_color=[0, 255, 128],  # Brighter green
        get_angle=0,
        # Adjust text anchor for better positioning
        get_text_anchor="'middle'",
        get_alignment_baseline="'center'"
    )
    # Title
    st.header("Darkwave Band Location :bat:", anchor="location")
    st.write("The city where the band started. Sometimes it will be the city that the band is associated with.")
    # Combine layers
    map = pdk.Deck(
        layers=[scatterplot_layer, text_layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    st.pydeck_chart(map)


def display_time_map(data):
    df = pd.DataFrame(data)

    current_year = datetime.now().year
    df['start_year'] = pd.to_numeric(df['start_year'], errors='coerce')
    df = df[(df['start_year'] >= 1975) & (df['start_year'] <= current_year)]

    # Sort DataFrame by start_year in ascending order
    df = df.sort_values(by='start_year', ascending=False)

    # Create custom y-ticks to space out band names
    y_ticks = range(len(df))
    band_names = df['band'].tolist()

    plt.figure(figsize=(15, max(8, len(y_ticks) * 0.5)))  # Adjust figure height based on number of bands
    plt.hlines(y=y_ticks, xmin=1975, xmax=df['start_year'], color='skyblue')
    plt.plot(df['start_year'], y_ticks, 'o', color='black')

    plt.yticks(ticks=y_ticks, labels=band_names, fontsize=20)  # Use custom y-ticks
    # Create x-axis ticks for every 5 years from 1975 to current year
    x_ticks = list(range(1975, current_year + 1, 5))
    if current_year not in x_ticks:  # Ensure the current year is included
        x_ticks.append(current_year)
    plt.xticks(ticks=x_ticks, fontsize=20)  # Increase font size for x-axis

    plt.xlabel('Start Year', fontsize=20)
    plt.ylabel('Band', fontsize=20)
    plt.title('Band Formation Timeline (1975 - Present)', fontsize=22)
    plt.grid(axis='x', which='both')  # Add grid lines for x-axis ticks
    plt.xlim(1975, current_year)

    st.header("Darkwave Band Time ⏲️", anchor="time")
    st.write("The year the band started.")

    st.pyplot(plt)

def layout(data):
    display_location_map(data)  # Function call to display the map
    display_time_map(data)  # Function call to display the chronological chart

def main():
    json_file_name = 'darkwave_bands.json'  # Replace with your JSON file name
    json_file_path = os.path.join(os.getcwd(), json_file_name)

    if os.path.exists(json_file_path):
        data = load_json_to_dict(json_file_path)
        # st.write("JSON Data:", data)
        layout(data)
    else:
        st.error(f"File {json_file_name} not found in the working directory.")

if __name__ == "__main__":
    st.title("Darkwave Project")
    st.write("Interesting Darkwave band information analysis.")
    main()
