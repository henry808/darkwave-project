import streamlit as st
import json
import os
import pandas as pd
import pydeck as pdk
import random


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

def display_map(data):
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

    # Combine layers
    map = pdk.Deck(
        layers=[scatterplot_layer, text_layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

    st.pydeck_chart(map)



def main():
    json_file_name = 'darkwave_bands.json'  # Replace with your JSON file name
    json_file_path = os.path.join(os.getcwd(), json_file_name)

    if os.path.exists(json_file_path):
        data = load_json_to_dict(json_file_path)
        # st.write("JSON Data:", data)
        display_map(data)  # Function call to display the map
    else:
        st.error(f"File {json_file_name} not found in the working directory.")

if __name__ == "__main__":
    st.title("Interactive Map Display App")
    main()