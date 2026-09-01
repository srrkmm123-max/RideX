from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from decimal import Decimal

from .gateway import create_payment_order

router = APIRouter()


class PaymentOrderRequest(BaseModel):
    amount: float
    currency: str = "INR"
    receipt: str = ""
    metadata: dict | None = None
    gateway_name: str | None = None


@router.get("/status")
async def status():
    return {
        "service": "payment-service",
        "status": "running"
    }


@router.post("/order")
async def create_order(request: PaymentOrderRequest):
    try:
        result = create_payment_order(
            amount=Decimal(str(request.amount)),
            currency=request.currency,
            receipt=request.receipt,
            metadata=request.metadata,
            gateway_name=request.gateway_name,
        )

        return {
            "success": True,
            "result": getattr(result, "__dict__", result),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
