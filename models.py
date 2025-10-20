from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: int
    speed: int

class Flight(BaseModel):
    flight_id: str
    airline: Optional[str]="Unknown"
    origin: Optional[str]="Unknown"
    destination: Optional[str]="Unknown"
    status: str = "in_air"
    last_update: Optional[datetime]
    updates: List[LocationUpdate] = Field(default_factory=list)
