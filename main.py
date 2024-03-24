# streamlit
# googlemaps
# requests
# streamlit-searchbbox
# pymongo
import streamlit as st
from streamlit_searchbox import st_searchbox
import requests
import googlemaps
import googlemaps.places
import googlemaps.distance_matrix
import pymongo 
import streamlit.components.v1 as components

mongo_client = pymongo.MongoClient(
    "mongodb+srv://:@emissions-hackathon-pro.l9weice.mongodb.net/?retryWrites=true&w=majority&appName=emissions-hackathon-proj"
)
google_key=
gmaps = googlemaps.Client(key=google_key)

car_specified = False
def car_suggestions(field, search_term):
    regex = f".*{search_term}.*"
    query = {field: {"$regex": regex, "$options": "i"}} 

    if field == 'make':
        query.update({'year': car_year})
    
    if field == 'model':
        query.update({'year': car_year})
        query.update({'make': car_make})
    
    return set([doc[field] for doc in mongo_client['vehicles-emissions']['vehicles'].find(query)])
with st.sidebar:
    st.header("Car Details")
    car_year = st.text_input(label="", placeholder="Year")
    if car_year: 
        car_make = st_searchbox(lambda search: car_suggestions('make', search), placeholder='Make', key='4')
        if car_make:
            car_model = st_searchbox(lambda search: car_suggestions('model', search), placeholder='Model', key='5')
            car_specified = True
if car_specified:
    result = mongo_client['vehicles-emissions']['vehicles'].find_one({'year': car_year, 'model': car_model, 'make': car_make})

route = False
def search_places(search_term):
    return [location['description'] for location in googlemaps.places.places_autocomplete(
        client=gmaps, input_text=search_term + " ", radius=50000)]

origin = st_searchbox(search_places, placeholder="Choose starting point...", key="1")
destination = st_searchbox(search_places, placeholder="Choose destination...", key="2")

if origin and destination:
    distance_matrix = googlemaps.distance_matrix.distance_matrix(client=gmaps, origins=origin, destinations=destination, mode='driving', units='imperial')
    distance_mi = distance_matrix['rows'][0]['elements'][0]['distance']['text']
    route = True


# Constants
CO2_OFFSET_PER_TREE_PER_YEAR = 48  # in pounds
GRAMS_PER_POUND = 454

if car_specified and route and result: 
    carbon_g = result['co2TailpipeGpm'] * float(distance_mi[:-3])
    total_emissions_pounds = carbon_g / GRAMS_PER_POUND

    trees_required = total_emissions_pounds / CO2_OFFSET_PER_TREE_PER_YEAR
    trees_required_rounded_up = int(trees_required) if trees_required.is_integer() else int(trees_required) + 1  # Round up to the nearest whole number

    if carbon_g < 1000:
        st.write(f"Total estimated CO2 emissions for driving {distance_mi}les in a {car_year} {car_make} {car_model}: {carbon_g:.2f} grams.")
    else:
        carbon_kg = carbon_g/1000
        st.write(f"Total estimated CO2 emissions for driving {distance_mi}les in a {car_year} {car_make} {car_model}: {carbon_kg:.2f} kilograms.")
    st.write(f"To offset these emissions, you would need to plant approximately {trees_required_rounded_up} tree(s).")

    origin_url = origin.replace(' ', '+')
    destination_url = destination.replace(' ', '+')

    embed_url = f"https://www.google.com/maps/embed/v1/directions?key={google_key}&origin={origin_url}&destination={destination_url}&mode=driving"

    st.markdown(f'<iframe width="600" height="450" frameborder="0" style="border:0" src="{embed_url}" allowfullscreen></iframe>',
                unsafe_allow_html=True)