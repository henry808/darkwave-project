import streamlit as st
import json
import os
import pandas as pd
import pydeck as pdk
# import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Function to load and apply CSS
def load_css(css_file):
    """
    Load and apply a CSS file to the Streamlit app.
    
    Args:
    - css_file (str): The path to the CSS file.
    """
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def stack_labels(df, key='band', offset=0.015):
    """
    Adjust the label positions in the DataFrame for better visualization.
    
    Args:
    - df (pandas.DataFrame): The DataFrame containing the data.
    - key (str, optional): The key column to use for stacking. Defaults to 'band'.
    - offset (float, optional): The offset to use for stacking labels. Defaults to 0.015.
    
    Returns:
    - pandas.DataFrame: The modified DataFrame with adjusted label positions.
    """
    # Group by the position and stack labels
    grouped = df.groupby(['latitude', 'longitude'])
    for (lat, lon), group in grouped:
        for i, (_, row) in enumerate(group.iterrows()):
            df.loc[row.name, 'stacked_latitude'] = lat + i * offset
    return df

def load_json_to_dict(file_path):
    """
    Load JSON data from a file into a dictionary.
    
    Args:
    - file_path (str): The path to the JSON file.
    
    Returns:
    - dict: The data loaded from the JSON file.
    """
    with open(file_path, 'r') as file:
        data_dicts = json.load(file)
    return data_dicts

def display_location_map(data):
    """
    Display a map with data points.
    
    Args:
    - data (dict): The data to display on the map.
    """
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


# Timeline graph
#
# Verticle graph lines at every 5 years starting with 1975
# Chronological order for bands (earliest at top)
# Year only Labels at each of 5 years.
# Height of graph at level showing all bands.


def display_time_map(data):
    df = pd.DataFrame(data)

    current_year = datetime.now().year
    df['start_year'] = pd.to_numeric(df['start_year'], errors='coerce')
    df = df.dropna(subset=['start_year'])
    df = df[(df['start_year'] >= 1975) & (df['start_year'] <= current_year)]

    if 'band' not in df.columns or df['band'].isnull().all():
        st.error("No valid 'band' data to display.")
        return

    # Sort data in reverse chronological order
    df = df.sort_values(by='start_year', ascending=True)

    # Calculate graph height
    graph_height = max(600, len(df) * 20)

    # Create Plotly figure
    fig = go.Figure()

    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['start_year'], current_year],
            y=[row['band'], row['band']],
            mode='lines',
            name=row['band'],
            showlegend=False  # Do not show legend for each line
        ))

    # Update x-axis for vertical grid lines every 5 years
    fig.update_xaxes(
        showgrid=True,            # Enable grid lines
        gridwidth=1,              # Set grid line width
        gridcolor='LightGrey',    # Set grid line color
        tickmode='linear',        # Set tick mode to linear for even distribution
        tick0=1975,               # Start ticks from 1975
        dtick=5,                  # Set tick interval to every 5 years
        tickformat="%Y",          # Format x-axis labels to show only year
        mirror=True,             # Mirror the ticks and labels to the top
    )

    # Update layout
    fig.update_layout(
        xaxis=dict(
            title='Year',
            tickmode='linear',
            tick0=1975,
            dtick=5,
            range=[1975, current_year]
        ),
        xaxis2=dict(
            overlaying="x", 
            side="top", 
            showgrid=False,
            tickformat="%Y",
            tickmode='linear',
            tick0=1975,
            dtick=5
        ),
        yaxis=dict(
            title='Band',
            autorange="reversed"  # Reverse the y-axis to have earliest bands on top
        ),
        title='Band Formation Timeline',
        title_font_size=22,
        font_size=20,
        height=graph_height
    )

    st.header("Band Formation Timeline")
    st.plotly_chart(fig, use_container_width=True)


# Function to display band information along with local image
def display_band_info(bands_data, debug):
    # Extract band names for the dropdown
    band_names = [band['band'] for band in bands_data]

    # Create a dropdown for selecting a band
    selected_band_name = st.selectbox("Select a band", band_names)

    # Find the selected band's data
    selected_band_data = next((band for band in bands_data if band['band'] == selected_band_name), None)

    # Display the selected band's information
    if selected_band_data:
        # Construct the path to the image
        file_name = selected_band_data['band'] + ".png"
        image_directory = "png"
        # image_path = os.path.join(os.getcwd(), image_directory, file_name)
        image_path = os.path.join(image_directory, file_name)
        if debug:
            st.write("image path = ", image_path)

        # Check if the image exists and then display it
        if os.path.exists(image_path):
            st.image(image_path, caption=selected_band_name)
        else:
            st.error(f"Image for {image_path} not found.")
        # Band Name
        st.write("Band Name:", selected_band_data['band'])
        st.write("Year Started:", selected_band_data['start_year'])
        st.write("City:", selected_band_data['city'])
        st.write("Country:", selected_band_data['country'])




def layout(data, debug, hide):

    css_file = 'style.css'
    if os.path.isfile(css_file):
        load_css(css_file)

    st.title("Darkwave Band Progression")
    st.write("Venture deep into the shadowy realms of Darkwave music, where echoes of the past intertwine with the pulse of the present..")

    display_location_map(data)  # Function call to display the map
    display_time_map(data)  # Function call to display the chronological chart
    display_band_info(data, debug) # Function to show one band.

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    if hide:
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def main():
    json_file_name = 'darkwave_bands.json'  # Replace with your JSON file name
    json_file_path = os.path.join(os.getcwd(), json_file_name)

    debug = False
    hide = False

    if os.path.exists(json_file_path):
        data = load_json_to_dict(json_file_path)
        # st.write("JSON Data:", data)
        layout(data, debug, hide)
    else:
        st.error(f"File {json_file_name} not found in the working directory.")

if __name__ == "__main__":
    main()
