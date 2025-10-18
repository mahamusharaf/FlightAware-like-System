from fastapi import FastAPI
from routes.flight_routes import router as flight_router

app = FastAPI(title="Flight Tracker System")

app.include_router(flight_router, prefix="/api/flights")

@app.get("/")
def root():
    return {"message": "Welcome to Flight Tracker!"}
