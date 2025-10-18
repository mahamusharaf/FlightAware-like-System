from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from database import flights_collection, flights_logs_collection
import folium
import os

router = APIRouter()
colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'darkred', 'darkgreen', 'cadetblue', 'lightred']

def generate_flight_map():
    flight_map = folium.Map(
        location=[30.3753, 69.3451],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    flights = list(flights_collection.find())
    for i, flight in enumerate(flights):
        updates = flight.get('updates', [])
        if not updates:
            continue

        coords = [(u['latitude'], u['longitude']) for u in updates]
        color = colors[i % len(colors)]
       # Draw flight path
        folium.PolyLine(
            coords,
            color=color,
            weight=3,
            opacity=0.7,
            tooltip=f"Flight: {flight.get('flight_id')}"
        ).add_to(flight_map)

        latest_update = updates[-1]
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0;">{flight.get('flight_id')}</h4>
            <b>Route:</b> {flight.get('origin', 'N/A')} → {flight.get('destination', 'N/A')}<br>
            <b>Airline:</b> {flight.get('airline', 'N/A')}<br>
            <b>Altitude:</b> {latest_update.get('altitude', 0)} ft<br>
            <b>Speed:</b> {latest_update.get('speed', 0)} knots<br>
            <b>Status:</b> {flight.get('status', 'Unknown')}<br>
            <b>Last Update:</b> {latest_update.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """

        folium.Marker(
            coords[-1],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{flight.get('flight_id')}",
            icon=folium.Icon(color=color, icon='plane', prefix='fa')
        ).add_to(flight_map)

        if len(coords) > 1:
            folium.CircleMarker(
                coords[0],
                radius=5,
                color=color,
                fill=True,
                fillOpacity=0.7,
                tooltip=f"Origin: {flight.get('origin', 'N/A')}"
            ).add_to(flight_map)

    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: auto; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
    <p style="margin: 0; font-weight: bold;">Active Flights: ''' + str(len(flights)) + '''</p>
    <p style="margin: 5px 0 0 0; font-size: 12px;">Map updates on page refresh</p>
    </div>
    '''
    flight_map.get_root().html.add_child(folium.Element(legend_html))

    flight_map.save("flight_map.html")
    return len(flights)


@router.get('/')
def welcome():
    return {'message': 'Flight Tracker API is running!'}


@router.post('/update')
def update_flight(data: dict):
    flight_id = data.get('flight_id')
    if not flight_id:
        raise HTTPException(status_code=400, detail="Flight ID is required")

    required_fields = ['timestamp', 'latitude', 'longitude', 'altitude', 'speed']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

    try:
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        if not (-90 <= lat <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid latitude or longitude format")

    update = {
        'timestamp': datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
        'latitude': float(data['latitude']),
        'longitude': float(data['longitude']),
        'altitude': float(data['altitude']),
        'speed': float(data['speed']),
    }

    flight = flights_collection.find_one({'flight_id': flight_id})
    if flight:
        flights_collection.update_one(
            {"flight_id": flight_id},
            {
                "$push": {"updates": update},
                "$set": {
                    "last_update": update["timestamp"],
                    "status": "in_air"
                }
            }
        )
        message = "Flight update added successfully"
    else:
        new_flight = {
            "flight_id": flight_id,
            "airline": data.get("airline", "Unknown"),
            "origin": data.get("origin", "Unknown"),
            "destination": data.get("destination", "Unknown"),
            "status": "in_air",
            "last_update": update["timestamp"],
            "created_at": datetime.utcnow(),
            "updates": [update]
        }
        flights_collection.insert_one(new_flight)
        message = "New flight created and update added successfully"
    try:
        generate_flight_map()
    except Exception as e:
        print(f"Map generation error: {e}")

    return {
        "success": True,
        "message": message,
        "flight_id": flight_id,
        "timestamp": data['timestamp'],
        "location": {
            "latitude": data['latitude'],
            "longitude": data['longitude'],
            "altitude": data['altitude']
        }
    }


@router.get('/map')
def get_map():
    if not os.path.exists("flight_map.html"):
        generate_flight_map()

    return FileResponse(
        "flight_map.html",
        media_type="text/html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@router.get('/flights')
def get_all_flights():

    flights = list(flights_collection.find())
    for flight in flights:
        flight['_id'] = str(flight['_id'])
        if 'last_update' in flight:
            flight['last_update'] = flight['last_update'].isoformat()
        if 'created_at' in flight:
            flight['created_at'] = flight['created_at'].isoformat()
        for update in flight.get('updates', []):
            if 'timestamp' in update:
                update['timestamp'] = update['timestamp'].isoformat()

    return {
        "success": True,
        "count": len(flights),
        "flights": flights
    }


@router.get('/{flight_id}')
def get_flight(flight_id: str, timestamp: str = None):
    flight = flights_collection.find_one({'flight_id': flight_id})
    if not flight:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
    if not flight.get("updates"):
        raise HTTPException(status_code=404, detail=f"No location updates available for flight {flight_id}")

    flight['_id'] = str(flight['_id'])

    if timestamp:

        try:
            target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400,
                                detail="Invalid timestamp format. Use ISO format (e.g., 2025-10-17T12:30:45)")

        closest = min(flight["updates"], key=lambda x: abs(x["timestamp"] - target_time))
        closest_copy = closest.copy()
        closest_copy['timestamp'] = closest_copy['timestamp'].isoformat()

        return {
            "success": True,
            "flight_id": flight_id,
            "airline": flight.get('airline'),
            "route": f"{flight.get('origin')} → {flight.get('destination')}",
            "requested_time": timestamp,
            "location": closest_copy,
            "time_difference_seconds": abs((closest['timestamp'] - target_time).total_seconds())
        }
    else:
        latest = flight["updates"][-1].copy()
        latest['timestamp'] = latest['timestamp'].isoformat()

        return {
            "success": True,
            "flight_id": flight_id,
            "airline": flight.get('airline'),
            "route": f"{flight.get('origin')} → {flight.get('destination')}",
            "status": flight.get('status'),
            "latest_location": latest,
            "total_updates": len(flight["updates"]),
            "tracking_duration": {
                "start": flight["updates"][0]['timestamp'].isoformat(),
                "end": flight["updates"][-1]['timestamp'].isoformat()
            }
        }


@router.put('/complete/{flight_id}')
def complete_flight(flight_id: str):
    flight = flights_collection.find_one({'flight_id': flight_id})

    if not flight:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
    flight["status"] = "landed"
    flight["completed_at"] = datetime.utcnow()
    flight["total_updates"] = len(flight.get("updates", []))

    if flight.get("updates"):
        first_update = flight["updates"][0]
        last_update = flight["updates"][-1]
        flight["flight_duration"] = (last_update["timestamp"] - first_update[
            "timestamp"]).total_seconds() / 3600  # hours
    flights_logs_collection.insert_one(flight)
    flights_collection.delete_one({"flight_id": flight_id})
    try:
        generate_flight_map()
    except Exception as e:
        print(f"Map generation error: {e}")

    return {
        "success": True,
        "message": f"Flight {flight_id} marked as completed and moved to logs",
        "total_updates": flight.get("total_updates", 0),
        "flight_duration_hours": flight.get("flight_duration", 0),
        "completed_at": flight["completed_at"].isoformat()
    }


@router.get('/logs/{flight_id}')
def get_flight_log(flight_id: str):
    flight = flights_logs_collection.find_one({'flight_id': flight_id})
    if not flight:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found in logs")

    # Convert ObjectId and datetime to JSON-serializable format
    flight['_id'] = str(flight['_id'])
    if 'completed_at' in flight:
        flight['completed_at'] = flight['completed_at'].isoformat()
    if 'last_update' in flight:
        flight['last_update'] = flight['last_update'].isoformat()
    if 'created_at' in flight:
        flight['created_at'] = flight['created_at'].isoformat()

    for update in flight.get('updates', []):
        if 'timestamp' in update:
            update['timestamp'] = update['timestamp'].isoformat()

    return {
        "success": True,
        "flight": flight
    }


@router.delete('/flights/{flight_id}')
def delete_flight(flight_id: str):
    result = flights_collection.delete_one({"flight_id": flight_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
    try:
        generate_flight_map()
    except Exception as e:
        print(f"Map generation error: {e}")

    return {
        "success": True,
        "message": f"Flight {flight_id} deleted successfully"
    }