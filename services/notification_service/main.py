"""
RideX Notification Service
"""

from fastapi import FastAPI


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="RideX Notification Service",
    description="RideX notification service",
    version="1.0.0"
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service": "notification-service",
        "status": "running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "service": "notification-service",
        "status": "healthy"
    }


# ============================================================
# SEND NOTIFICATION
# ============================================================

@app.post("/notifications")
def send_notification(
    user_id: int,
    message: str,
    notification_type: str = "push"
):

    return {
        "status": "sent",
        "user_id": user_id,
        "type": notification_type,
        "message": message
    }
