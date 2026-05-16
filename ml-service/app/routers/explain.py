from fastapi import APIRouter

router = APIRouter()

@router.post("/explain")
async def explain():
    return {"message": "Explain endpoint ready"}
