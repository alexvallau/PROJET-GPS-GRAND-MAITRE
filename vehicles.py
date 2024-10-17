import requests
from flask import Blueprint, render_template

# Chargetrip API details
CHARGETRIP_API_URL = 'https://api.chargetrip.io/graphql'
CHARGETRIP_API_KEY = '670f71d6021ae87118926aa3'
CHARGETRIP_API_APPID= '670f71d6021ae87118926aa5'

vehicles_bp = Blueprint('vehicles', __name__)



def get_vehicles():
    url = "https://api.chargetrip.io/graphql"
    headers = {
        "Content-Type": "application/json",
        "x-client-id": CHARGETRIP_API_KEY,
        "x-app-id": CHARGETRIP_API_APPID
    }
    query = """
    {
      carList {
        id
        naming {
          make
          model
          version
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
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        vehicles = response.json()['data']['carList']
        # Afficher les données pour vérification
       
        return vehicles
    else:
        return []