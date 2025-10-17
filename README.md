# FlightAware-like-System

# MongoDB Schema Design

## flights collection
{
  flight_id: String,
  airline: String,
  origin: String,
  destination: String,
  status: String,     // "in_air" or "landed"
  last_update: Date,
  updates: [
    {
      timestamp: Date,
      latitude: Number,
      longitude: Number,
      altitude: Number,
      speed: Number
    }
  ]
}

## flight_logs collection
{
  flight_id: String,
  airline: String,
  origin: String,
  destination: String,
  status: "landed",
  duration: Number,
  updates: [ ... ]  // all flight points
}
