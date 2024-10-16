import requests
from flask import Blueprint, render_template

# Chargetrip API details
CHARGETRIP_API_URL = 'https://api.chargetrip.io/graphql'
CHARGETRIP_API_KEY = 'your_chargetrip_api_key'

vehicles_bp = Blueprint('vehicles', __name__)

def get_electric_vehicles():
    query = """
    {
        vehicleList {
            id
            make
            model
            battery {
                usable_kwh
            }
            range {
                chargetrip_range {
                    best
                    worst
                }
            }
        }
    }
    """
    headers = {
        'Content-Type': 'application/json',
        'x-client-id': CHARGETRIP_API_KEY
    }
    response = requests.post(CHARGETRIP_API_URL, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['vehicleList']
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")

@vehicles_bp.route('/vehicles')
def vehicles():
    try:
        vehicles = get_electric_vehicles()
        return render_template('vehicles.html', vehicles=vehicles)
    except Exception as e:
        return render_template('vehicles.html', vehicles=None, error=str(e))