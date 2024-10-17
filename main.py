import folium
import flask
import openrouteservice
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from vehicles import get_vehicles  # Import the function
from bornes import get_stations_around  # Import the function
import geopy.distance
import logging

# Initialize the Flask application
app = flask.Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenRouteService client
ors_client = openrouteservice.Client(key='5b3ce3597851110001cf62480196e265957844a2b9f38d55301e417c')

@app.route('/')
def index():
    vehicles = get_vehicles()
    m = folium.Map(location=(45.5236, -122.6750))
    map_html = m._repr_html_()
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
        # Get the initial route
        route = ors_client.directions(coordinates=coords, profile='driving-car', format='geojson')
        distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert to kilometers
        
        vehicles = get_vehicles()
        vehicle_data = next((v for v in vehicles if v['id'] == vehicle_id), None)
        max_autonomy = vehicle_data['range']['chargetrip_range']['best']
        max_distance = max_autonomy - 15  # 15 km safety margin
        
        route_coords = route['features'][0]['geometry']['coordinates']
        modified_route_coords = []  # To store the modified route with detours
        nearest_stations = []  # Store all nearest stations along the route

        current_index = 0
        
        while current_index < len(route_coords) - 1:
            next_index = current_index
            cumulative_distance = 0
            
            # Find next point within vehicle's max autonomy range
            while next_index < len(route_coords) - 1 and cumulative_distance < max_distance:
                point1 = route_coords[next_index]
                point2 = route_coords[next_index + 1]
                segment_distance = geopy.distance.distance((point1[1], point1[0]), (point2[1], point2[0])).km
                cumulative_distance += segment_distance
                next_index += 1
            
            # Search for stations around the next coordinate
            coord = route_coords[next_index]
            stations = get_stations_around(coord)
            nearest_station = None
            min_distance = float('inf')
            
            # Find nearest station
            for station in stations:
                if 'location' in station and 'coordinates' in station['location']:
                    station_distance = geopy.distance.distance(
                        (station['location']['coordinates'][1], station['location']['coordinates'][0]),
                        (coord[1], coord[0])
                    ).km
                    if station_distance < min_distance:
                        min_distance = station_distance
                        nearest_station = station
            
            if nearest_station:
                # Add the nearest station to the list
                nearest_stations.append(nearest_station)
                
                # Route to the charging station
                station_coord = nearest_station['location']['coordinates']
                station_route_to = ors_client.directions(coordinates=[route_coords[current_index], station_coord], profile='driving-car', format='geojson')
                station_route_to_coords = station_route_to['features'][0]['geometry']['coordinates']
                
                # Route from the charging station back to the next point on the original route
                station_route_back = ors_client.directions(coordinates=[station_coord, route_coords[next_index]], profile='driving-car', format='geojson')
                station_route_back_coords = station_route_back['features'][0]['geometry']['coordinates']
                
                # Append detour to the modified route
                modified_route_coords.extend(station_route_to_coords)
                modified_route_coords.extend(station_route_back_coords)
            else:
                # No station found, proceed with original route
                modified_route_coords.append(route_coords[next_index])
            
            current_index = next_index
        
        # Create the map with the modified route
        m = folium.Map(location=[(location1.latitude + location2.latitude) / 2, (location1.longitude + location2.longitude) / 2], zoom_start=6)
        
        # Draw the modified route
        folium.PolyLine([(coord[1], coord[0]) for coord in modified_route_coords], color='blue').add_to(m)
        
        # Mark nearest charging stations on the map
        for station in nearest_stations:
            if 'location' in station and 'coordinates' in station['location']:
                folium.Marker(
                    location=[station['location']['coordinates'][1], station['location']['coordinates'][0]],
                    popup=f"{station['name'] if 'name' in station else 'Unknown'}<br>{station['address'] if 'address' in station else 'No address'}",
                    icon=folium.Icon(color='red', icon='bolt')
                ).add_to(m)
        
        map_html = m._repr_html_()
        
        return flask.render_template('index.html', map_html=map_html, vehicles=vehicles, distance=distance, vehicle_data=vehicle_data, error=None)
    
    except openrouteservice.exceptions.ApiError as e:
        error_message = str(e)
        logging.error(f"API error: {error_message}")
        vehicles = get_vehicles()
        return flask.render_template('index.html', map_html=None, vehicles=vehicles, distance=None, vehicle_data=None, error=error_message)
    

if __name__ == '__main__':
    app.run(debug=True)
