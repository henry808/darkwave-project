import streamlit as st
import json
import os
import pandas as pd
import pydeck as pdk
# import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_option_menu import option_menu  # Additional library for horizontal menu
import streamlit.components.v1 as components



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

def display_home():
    st.write("Venture deep into the shadowy realms of Darkwave music, where echoes of the past intertwine with the pulse of the present..")
    st.write("")
    st.write("This website has some data analytics about darkwave bands. See the following resources available:")
    st.write("")
    st.write("1. Map with darkwave bands' locations.")
    st.write("")
    st.write("2. Timeline with start time of darkwave bands in chronological order.")
    st.write("")
    st.write("3. Band information.")
    st.write("")
    st.write("4. Influence chart (coming soon).")
    st.write("")
    st.write("Choose in the menu above.")

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


def display_time_chart(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Get current year and filter data
    current_year = datetime.now().year
    df['start_year'] = pd.to_numeric(df['start_year'], errors='coerce')
    df = df.dropna(subset=['start_year'])
    df = df[(df['start_year'] >= 1975) & (df['start_year'] <= current_year)]

    # Check for valid 'band' data
    if 'band' not in df.columns or df['band'].isnull().all():
        st.error("No valid 'band' data to display.")
        return

    # Sort DataFrame in ascending order by 'start_year'
    df = df.sort_values(by='start_year', ascending=True)

    # Set graph height dynamically based on data
    graph_height = max(600, len(df) * 20)

    # Initialize Plotly figure
    fig = go.Figure()

    # Add data points to the figure
    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['start_year']],
            y=[row['band']],
            mode='markers+text',  # Enable both markers and text
            text=[str(row['start_year'])],  # Set text label as the year
            textposition="middle right",    # Position text to the right of the marker
            marker=dict(size=10),           # Define marker size
            showlegend=False                # Disable the legend
        ))

    # Update x-axis configuration
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGrey',
        tickmode='linear',
        tick0=1975,
        dtick=5,
        tickformat="%Y",
        mirror=True,
        range=[1974, current_year + 1]  # Extend x-axis range to accommodate labels
    )

    # Update overall layout of the figure
    fig.update_layout(
        xaxis=dict(
            title='Year',
            tickmode='linear',
            tick0=1975,
            dtick=5,
            range=[1974, current_year + 1]  # Extend x-axis range for label visibility
        ),
        yaxis=dict(
            title='Band',
            autorange="reversed"
        ),
        title='Band Formation Timeline',
        title_font_size=22,
        font_size=20,
        height=graph_height,
        margin=dict(r=50)  # Adjust right margin to ensure labels fit
    )

    # Display the chart in Streamlit
    st.header("Band Formation Timeline")
    st.plotly_chart(fig, use_container_width=True)


# Function to display band information along with local image
def display_band_info(bands_data, image_directory, pic_width, debug):
    # Extract band names for the dropdown
    band_names = [band['band'] for band in bands_data]

    band_names.sort()

    # Create a dropdown for selecting a band
    selected_band_name = st.selectbox("Select a band", band_names)

    # Find the selected band's data
    selected_band_data = next((band for band in bands_data if band['band'] == selected_band_name), None)

    # Display the selected band's information
    if selected_band_data:
        # Construct the paths to the images
        file_name_png = selected_band_data['band'] + ".png"
        file_name_jpg = selected_band_data['band'] + ".jpg"

        image_path_png = os.path.join(image_directory, file_name_png)
        image_path_jpg = os.path.join(image_directory, file_name_jpg)

        if debug:
            st.write("PNG image path = ", image_path_png)
            st.write("JPG image path = ", image_path_jpg)

        # Check if the PNG image exists and then display it
        if os.path.exists(image_path_png):
            st.image(image_path_png, width=pic_width, caption=selected_band_name)
        # If PNG does not exist, check for JPG
        elif os.path.exists(image_path_jpg):
            st.image(image_path_jpg, width=pic_width, caption=selected_band_name)
        else:
            if debug:
                st.error(f"Image for {selected_band_name} not found.")
            else:
                file_name_jpg = "Darkwave Band.jpg"
                image_path_jpg = os.path.join(image_directory, file_name_jpg)
                st.image(image_path_jpg, width=pic_width, caption='Placeholder Image')       

        # Band Name
        st.write("Band Name:", selected_band_data['band'])
        st.write("Year Started:", str(selected_band_data['start_year']))
        st.write("City:", selected_band_data['city'])
        st.write("Country:", selected_band_data['country'])

        # affiliate marketing testing
        if selected_band_data['band'] == "Joy Division":
            # This did not work right:
            # st.components.v1.html('<a href="https://www.amazon.com/Joy-Division-Official-Stacked-Pleasures/dp/B0C4CFSQCZ?th=1&psc=1&linkCode=ll1&tag=darkwave0e-20&linkId=b3a2898627699ccd66c805f92e1f7976&language=en_US&ref_=as_li_ss_tl">Joy Division Store</a>')
            # st.components.v1.html('<a href="https://amzn.to/3SRSdpu">Unknown Pleasures Vinyl LP</a>')
            # st.components.v1.html('<a href="https://www.geeksforgeeks.org/beautifulsoup-installation-python/">Geek</a>')

            url = "https://amzn.to/3SRSdpu"
            st.write("Joy Div [link](%s)" % url)
            st.markdown("check out this [link](%s)" % url)

            url = "https://www.geeksforgeeks.org/beautifulsoup-installation-python/"
            st.write("Geeks [link](%s)" % url)
            st.markdown("check out this [link](%s)" % url)


def layout(data, image_directory, pic_width, debug, hide):

    css_file = 'style.css'
    if os.path.isfile(css_file):
        load_css(css_file)

    st.title("Darkwave Band Exploration")

    # Horizontal Menu
    selected = option_menu("Main Menu",
                        ['Home', 'Map', 'Time Graph', 'Band Information'],
                        icons=['house', 'globe-americas','calendar', 'info-circle-fill'],
                        menu_icon='cast',
                        default_index=0,
                        orientation='horizontal',
                        styles={
                            "container": {"font-family": "Bradley Gratis"},
                            "menu-title": {"font-family": "Bradley Gratis"},
                            "nav": {"font-family": "Bradley Gratis"},
                            "nav-item": {"font-family": "Bradley Gratis"},
                            "nav-link": {"font-family": "Bradley Gratis"},
                            "nav-link-selected": {"font-family": "Bradley Gratis"},
                            "icon": {"font-family": "Bradley Gratis"},
                            "separator": {"font-family": "Bradley Gratis"},
                            }
                        )
    if selected == "Home":
        display_home()
    elif selected == "Map":
        display_location_map(data)  # Function call to display the map
    elif selected == "Time Graph":
        display_time_chart(data)  # Function call to display the chronological chart
    elif selected == "Band Information":
        display_band_info(data, image_directory, pic_width, debug) # Function to show one band.

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    if hide:
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def main():
    # Configuration
    json_file_name = 'darkwave_bands.json'  # Replace with your JSON file name
    image_directory = "png"
    pic_width = 500
    debug = False
    hide = False

    # get data and create layout
    json_file_path = os.path.join(os.getcwd(), json_file_name)
    if os.path.exists(json_file_path):
        data = load_json_to_dict(json_file_path)
        if debug:
            # st.write("JSON Data:", data)
            pass
        layout(data, image_directory, pic_width, debug, hide)
    else:
        st.error(f"File {json_file_name} not found in the working directory.")

if __name__ == "__main__":
    main()
