import os
import logging
from flask import Blueprint, request, jsonify
import googlemaps
from pydantic import BaseModel, Field, ValidationError
from typing import List

logger = logging.getLogger(__name__)

# --- Pydantic Model for Request ---
class LocationRequest(BaseModel):
    latitude: float = Field(..., description="User's latitude")
    longitude: float = Field(..., description="User's longitude")

# --- Pydantic Model for Response ---
class Hospital(BaseModel):
    name: str
    address: str # 'vicinity' from Google API is often the address

class HospitalResponse(BaseModel):
    hospitals: List[Hospital]

# --- Blueprint ---
misc_bp = Blueprint('misc', __name__, url_prefix='/api/misc')

@misc_bp.route('/find_hospitals', methods=['POST'])
def find_nearby_hospitals():
    """
    Finds nearby hospitals based on user's latitude and longitude.
    """
    try:
        data = LocationRequest(**request.get_json())
    except ValidationError as e:
        logger.error(f"Location request validation error: {e.json()}")
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Invalid JSON data: {e}")
        return jsonify({"error": f"Invalid JSON data: {e}"}), 400

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY is not set. Cannot search for hospitals.")
        return jsonify({'error': 'Server configuration error: Missing API key'}), 500

    try:
        gmaps = googlemaps.Client(key=api_key)
        
        logger.info(f"Searching for hospitals near ({data.latitude}, {data.longitude})")
        
        places_result = gmaps.places_nearby(
            location=(data.latitude, data.longitude),
            radius=10000,  # 10km radius
            type='hospital'
        )

        results = places_result.get('results', [])
        hospital_list = []

        for place in results:
            hospital_list.append(
                Hospital(
                    name=place.get('name', 'N/A'),
                    address=place.get('vicinity', 'Address not available')
                )
            )
        
        logger.info(f"Found {len(hospital_list)} hospitals.")
        response_data = HospitalResponse(hospitals=hospital_list)
        return jsonify(response_data.model_dump())

    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error: {e}")
        return jsonify({'error': f'Google Maps API error: {e}'}), 500
    except Exception as e:
        logger.error(f"Error finding hospitals: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
