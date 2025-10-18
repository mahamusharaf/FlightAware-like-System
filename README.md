FlightAware-like System

A mini Flight Tracking System built using FastAPI and MongoDB.
It simulates a real-time radar that receives flight updates, stores them in a database, and visualizes flight paths on an interactive Folium map.

 Overview

This system tracks flights in real-time by:

Receiving live position updates (latitude, longitude, altitude, speed)

Storing them in MongoDB

Displaying active flights and their routes on a dynamic map (/map)

📡 API Endpoints
GET /

→ Returns a welcome message (verifies API is running)

POST /update

→ Adds or updates a flight’s location and details
→ Creates a new record if the flight doesn’t exist

GET /flights

→ Fetches all active flights with their tracking data

GET /{flight_id}

→ Retrieves a specific flight’s latest or timestamp-based location

PUT /complete/{flight_id}

→ Marks a flight as completed (landed) and moves it to logs

GET /logs/{flight_id}

→ Fetches data for a completed (landed) flight

DELETE /flights/{flight_id}

→ Deletes a flight and refreshes the map

GET /map

→ Displays the live map with all active flight routes

🧾 Example Input (JSON)
{
  "flight_id": "PK303",
  "timestamp": "2025-10-14T08:00:00",
  "latitude": 31.55,
  "longitude": 74.34,
  "altitude": 35000,
  "speed": 850,
  "airline": "Pakistan International Airlines",
  "origin": "LHE",
  "destination": "KHI"
}
