import requests

CHARGETRIP_API_KEY = '670f71d6021ae87118926aa3'
CHARGETRIP_API_APPID = '670f71d6021ae87118926aa5'
CHARGETRIP_API_URL = 'https://api.chargetrip.io/graphql'  # Assuming this is the correct URL

def get_stations_around(coord, radius_km=10):
    graphql_query = """
    query stationAround($query: StationAroundQuery!) {
      stationAround(query: $query, size: 100) {
        location {
          type
          coordinates
        }
        power
        speed
        status
      }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-id': CHARGETRIP_API_KEY,
        'x-app-id': CHARGETRIP_API_APPID
    }
    
    variables = {
        "query": {
            "location": {
                "type": "Point",
                "coordinates": [coord[0], coord[1]]  # Note: longitude first, then latitude
            },
            "distance": radius_km * 1000  # Convert km to meters
        }
    }
    
    response = requests.post(CHARGETRIP_API_URL, json={'query': graphql_query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        #print("Mes stations sont:", response.json())
        return response.json()['data']['stationAround']  # Ensure you're returning the correct data
    else:
        raise Exception(f"Query failed to run by returning code {response.status_code}. {response.text}")

