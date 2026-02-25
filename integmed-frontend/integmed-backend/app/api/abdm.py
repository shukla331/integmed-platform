"""ABDM Integration API - stub for ABDM endpoints"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/status")
async def abdm_status():
    return {"status": "connected", "version": "v3"}
