# streamlit
# googlemaps
# requests
# streamlit-searchbox
# pymongo
import streamlit as st
from streamlit_searchbox import st_searchbox
import googlemaps
import googlemaps.places
import googlemaps.distance_matrix
import googlemaps.geocoding
from googlemaps import convert
import pymongo
import certifi
ca = certifi.where()
import FindNearestIntersection as FN

st.title("Walk For Groot")
with st.expander("## How to Use"):
    st.write(
        """
        To use this app, first specify the year, make, and model of your vehicle in the sidebar. 
        Next, input your starting point and end destination. 
        This will show your estimated carbon emissions, as well the number of Baby Groots needed to offset these emissions.
        Select a reduced amount of carbon emissions in the slider and click the button labeled 'Calculate New Drop Off Location'
        in order to see a new path that will result in reduced carbon emissions. Happy walking!
        """
    )

mongo_client = pymongo.MongoClient(
    f"mongodb+srv://{st.secrets['username']}:{st.secrets['password']}@emissions-hackathon-pro.l9weice.mongodb.net/?retryWrites=true&w=majority&appName=emissions-hackathon-proj", tlsCAFile=ca)
google_key=st.secrets['google']
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
    result = mongo_client['vehicles-emissions']['vehicles'].find_one(
        {'year': car_year, 'model': car_model, 'make': car_make})

route = False

def search_places(search_term):
    return [location['description'] for location in googlemaps.places.places_autocomplete(
        client=gmaps, input_text=search_term + " ", radius=50000)]


origin = st_searchbox(search_places, placeholder="Choose starting point...", key="1")
destination = st_searchbox(search_places, placeholder="Choose destination...", key="2")

if origin and destination:
    try:
        distance_matrix = googlemaps.distance_matrix.distance_matrix(client=gmaps, origins=origin, destinations=destination,
                                                                    mode='driving', units='imperial')
        distance_mi = distance_matrix['rows'][0]['elements'][0]['distance']['text']
        route = True
    except:
        st.write("No Path Found")
        st.stop()

# Constants
CO2_OFFSET_PER_TREE_PER_YEAR = 48 # in pounds
GRAMS_PER_POUND = 454

if car_specified and route and result:
    carbon_g = result['co2TailpipeGpm'] * float("".join(distance_mi.split(","))[:-3])
    total_emissions_pounds = carbon_g / GRAMS_PER_POUND

    trees_required = total_emissions_pounds / CO2_OFFSET_PER_TREE_PER_YEAR*100
    trees_required_rounded_up = int(trees_required) if trees_required.is_integer() else int(
        trees_required) + 1  # Round up to the nearest whole number

    st.write(f"### Distance: {distance_mi}les.")
    if carbon_g < 1000:
        st.write(f"### Total estimated CO2 emissions: {carbon_g:.2f} grams.")
    else:
        carbon_kg = carbon_g / 1000
        st.write(f"### Total estimated CO2 emissions: {carbon_kg:.2f} kilograms.")
    st.write(f"### Offseting this requires planting ~{trees_required_rounded_up} baby groot(s).")
    origin_url = origin.replace(' ', '+')
    destination_url = destination.replace(' ', '+')

    embed_url = f"https://www.google.com/maps/embed/v1/directions?key={google_key}&origin={origin_url}&destination={destination_url}&mode=driving"

    st.markdown(
        f'<iframe width="700" height="500" frameborder="0" style="border:0" src="{embed_url}" allowfullscreen></iframe>',
        unsafe_allow_html=True)

    if carbon_g == 0:
        st.stop()
    # -------------------------- Sliders ----------------------------

    initialCO2 = carbon_g  # grams
    initialTrees = trees_required_rounded_up
    color = (255, 0, 0)

    CO2 = initialCO2
    trees = initialTrees

    greenPercentage = 0.5


    def updateCO2():
        st.session_state.trees = int(st.session_state.CO2 / GRAMS_PER_POUND / CO2_OFFSET_PER_TREE_PER_YEAR*100)
        # updateColor()


    def updateTrees():
        st.session_state.CO2 = st.session_state.trees * CO2_OFFSET_PER_TREE_PER_YEAR * GRAMS_PER_POUND/100
        # updateColor()


    def updateColor():
        global color
        color = (255 * (CO2 / initialCO2 - greenPercentage) / (1 - greenPercentage),
                 255 * (1 - CO2 / initialCO2) / (1 - greenPercentage), 0)

    st.write("#### CO2")
    CO2 = st.slider("", value=CO2, min_value= initialCO2 * 0.8, max_value=initialCO2, on_change=updateCO2, key="CO2")
    st.write(CO2, '**Carbon emission in grams.**')

    st.write("#### Baby Groots")
    trees = st.slider('', value=int(trees), min_value=int(0.8*initialTrees), max_value=int(initialTrees), on_change=updateTrees, key="trees",
                      step=1)
    st.write(trees, '**Baby Groots required to offset. (1 Baby Groot = 1/100th of a tree, or Big Groot!)**')

    ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
        background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html=True)

    Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
        background-color: rgb(255,255,255); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''',
                                unsafe_allow_html=True)

    Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                    { color: rgb(255,255,255); } </style>''', unsafe_allow_html=True)

    col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
        background: linear-gradient(to right, rgb(0, 255, 0) {greenPercentage * 100}%, 
                                    rgb(255, 0, 0) 100%, 
                                    rgba(255, 166, 195, 0.25) {CO2/initialCO2 * 100}%, 
                                    rgba(151, 166, 195, 0.25) 100%); }} </style>'''

    ColorSlider = st.markdown(col, unsafe_allow_html=True)

    # -------------------

    def geocode(client, address=None, place_id=None, components=None, bounds=None, region=None,
                language=None):

        params = {}

        if address:
            params["address"] = address

        if place_id:
            params["place_id"] = place_id

        if components:
            params["components"] = convert.components(components)

        if bounds:
            params["bounds"] = convert.bounds(bounds)

        if region:
            params["region"] = region

        if language:
            params["language"] = language

        return client._request("/maps/api/geocode/json", params)['results'][0]['geometry']['location']

    print()

    if st.button('**Calculate New Drop Off Location**'):
        coordD = geocode(gmaps, address=destination)
        latD, lngD = coordD["lat"], coordD["lng"]

        coordS = geocode(gmaps, address=origin)
        latS, lngS = coordS["lat"], coordS["lng"]

        newDest, address = FN.giveNearestAddress(latD, lngD, latS, lngS, 3000, float("".join(distance_mi.split(","))[:-3]) * 1.6 * (1 - CO2/initialCO2))

        # st.write(newDest)

        if newDest == [0, 0]:
            newDest = [latD, lngD]

        # st.write(latD, lngD, latS, lngS, 500, float(distance_mi[:-2]) * 1.6 * (1 - CO2/initialCO2))

        origin_url = origin.replace(' ', '+')

        embed_url = f"https://www.google.com/maps/embed/v1/directions?key={google_key}&origin={origin_url}&destination={newDest[0]},{newDest[1]}&mode=driving"

        st.markdown(
            f'<iframe width="700" height="500" frameborder="0" style="border:0" src="{embed_url}" allowfullscreen></iframe>',
            unsafe_allow_html=True)
        
        embed_url = f"https://www.google.com/maps/embed/v1/directions?key={google_key}&origin={newDest[0]},{newDest[1]}&destination={destination_url}&mode=walking"

        st.markdown(
            f'<iframe width="700" height="500" frameborder="0" style="border:0" src="{embed_url}" allowfullscreen></iframe>',
            unsafe_allow_html=True)

        st.write(f"#### You have saved {initialTrees - trees} Baby Groots by going to {address if len(address) > 0 else destination}!")


