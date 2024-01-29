# darkwave-project

## Name
Darkwave Project

## Description
Webapp with scatter map, chronological chart, etc. for darkwave bands.

## Intro

## Installing
Clone repo 
```
cd <existing git repo>
git clone <this repo>
```
### Prerequisites
1. git
2. conda

### Condo setup
```bash
conda create -n darkwave-project python=3.11
conda install conda-forge::streamlit
conda install conda-forge::matplotlib
conda install conda-forge::geopy
conda install conda-forge::pydeck
conda install conda-forge::pandas
conda install conda-forge::streamlit-option-menu
# conda install conda-forge::plotly
```

## Activating Condo
```bash
# To activate this environment, use
conda activate darkwave-project

# To deactivate an active environment
conda deactivate
```

## Usage
Run local in a web browser on `http://localhost:8501/`
Can run from VSC or other IDE with this command:
```bash
streamlit run c:<git folder path>\darkwave-project\streamlit_app.py
```







## geoply testing (for testing issues with entries)
Run python in anaconda window and then use these commands:
```
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
location = geolocator.geocode("175 5th Avenue NYC")
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)
```

## ToDo
1. Fix bands that show up in middle
2. Add more bands
3. Add chronological graph
4. Add Influence graph
5. Better tooltip display
6. Fix style


## Support
Github issue

## Roadmap
I am considering working on an influence chart.

## Authors and acknowledgment
Henry Grantham

## License
ToDo

## Project status
WIP
