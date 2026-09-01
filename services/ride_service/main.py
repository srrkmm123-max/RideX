from fastapi import FastAPI

app = FastAPI(
    title="RideX Ride Service",
    description="Ride booking and ride management service",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "service": "ride-service",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ride-service"
    }

@app.get("/rides")
def get_rides():
    return {
        "rides": []
    }

@app.get("/rides/{ride_id}")
def get_ride(ride_id: int):
    return {
        "ride_id": ride_id
    }

@app.post("/rides")
def create_ride(ride: dict):
    return {
        "message": "Ride created",
        "ride": ride
    }

@app.put("/rides/{ride_id}/status")
def update_ride_status(ride_id: int, status: str):
    return {
        "ride_id": ride_id,
        "status": status
    }

@app.delete("/rides/{ride_id}")
def cancel_ride(ride_id: int):
    return {
        "ride_id": ride_id,
        "status": "cancelled"
    }
