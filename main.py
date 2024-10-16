import folium
import flask
import openrouteservice
from geopy.geocoders import Nominatim

# Initialize the Flask application
app = flask.Flask(__name__)

# Initialize OpenRouteService client
ors_client = openrouteservice.Client(key='5b3ce3597851110001cf6248c7cfeb0c65f04db79d105b547b63d1f2')

# Define a route to serve the main page
@app.route('/')
def index():
    # Create the map
    m = folium.Map(location=(45.5236, -122.6750))
    map_html = m._repr_html_()
    
    # Render the template with the map HTML
    return flask.render_template('index.html', map_html=map_html)

# Define a route to calculate and display the route
@app.route('/route')
def route():
    city1 = flask.request.args.get('city1')
    city2 = flask.request.args.get('city2')
    
    geolocator = Nominatim(user_agent="route_app")
    location1 = geolocator.geocode(city1)
    location2 = geolocator.geocode(city2)
    
    coords = ((location1.longitude, location1.latitude), (location2.longitude, location2.latitude))
    route = ors_client.directions(coordinates=coords, profile='driving-car', format='geojson')
    
    # Create the map
    m = folium.Map(location=[(location1.latitude + location2.latitude) / 2, (location1.longitude + location2.longitude) / 2], zoom_start=6)
    folium.GeoJson(route).add_to(m)
    map_html = m._repr_html_()
    
    return map_html

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)