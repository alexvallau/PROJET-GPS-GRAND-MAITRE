import folium
import flask
import openrouteservice
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from vehicles import get_vehicles  # Import the function

# Initialize the Flask application
app = flask.Flask(__name__)

# Initialize OpenRouteService client
ors_client = openrouteservice.Client(key='5b3ce3597851110001cf6248c7cfeb0c65f04db79d105b547b63d1f2')

# Define a route to serve the main page
@app.route('/')
def index():
    # Fetch the list of vehicles
    vehicles = get_vehicles()
    
    # Create the map
    m = folium.Map(location=(52.30, 21))
    map_html = m._repr_html_()
    
    # Render the template with the map HTML and vehicles
    return flask.render_template('index.html', map_html=map_html, vehicles=vehicles, distance=None, vehicle_data=None, error=None)

def geocode_with_retry(geolocator, city, retries=2):
    for _ in range(retries):
        try:
            return geolocator.geocode(city, timeout=2)
        except GeocoderTimedOut:
            continue
    return None

# Define a route to calculate and display the route
@app.route('/route')
def route():
    city1 = flask.request.args.get('city1')
    city2 = flask.request.args.get('city2')
    vehicle_id = flask.request.args.get('vehicle_id')
    
    geolocator = Nominatim(user_agent="route_app")
    location1 = geocode_with_retry(geolocator, city1)
    location2 = geocode_with_retry(geolocator, city2)
    
    if not location1 or not location2:
        error_message = "Geocoding service is unavailable. Please try again later."
        vehicles = get_vehicles()
        return flask.render_template('index.html', map_html=None, vehicles=vehicles, distance=None, vehicle_data=None, error=error_message)
    
    coords = ((location1.longitude, location1.latitude), (location2.longitude, location2.latitude))
    
    try:
        route = ors_client.directions(coordinates=coords, profile='driving-car', format='geojson')
        # Extract distance from the route
        distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert to kilometers
        
        # Fetch the list of vehicles
        vehicles = get_vehicles()
        
        # Find the selected vehicle data
        vehicle_data = next((v for v in vehicles if v['id'] == vehicle_id), None)
        
        # Create the map
        m = folium.Map(location=[(location1.latitude + location2.latitude) / 2, (location1.longitude + location2.longitude) / 2], zoom_start=6)
        folium.GeoJson(route).add_to(m)
        map_html = m._repr_html_()
        
        return flask.render_template('index.html', map_html=map_html, vehicles=vehicles, distance=distance, vehicle_data=vehicle_data, error=None)
    except openrouteservice.exceptions.ApiError as e:
        error_message = str(e)
        vehicles = get_vehicles()
        return flask.render_template('index.html', map_html=None, vehicles=vehicles, distance=None, vehicle_data=None, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)