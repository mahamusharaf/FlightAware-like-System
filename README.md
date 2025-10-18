# FlightAware-like-System
A mini Flight Tracking System built using FastAPI and MongoDB.
It simulates a real-time radar system that receives flight updates, stores them in a database, and displays flight paths on an interactive Folium map.
📡 API Endpoints
GET /
Welcome message (verifies API is running)
POST /update
Adds or updates a flight’s location and details (creates a new flight if not found)
GET /flights
Returns all active flights with their tracking data
GET /{flight_id}
Returns the latest or timestamp-based location of a specific flight
PUT /complete/{flight_id}
Marks a flight as completed and moves it to flight logs
GET /logs/{flight_id}
Fetches data of a completed (landed) flight
DELETE /flights/{flight_id}
Deletes a flight record and updates the map
GET /map
Displays live flight map with all active routes
