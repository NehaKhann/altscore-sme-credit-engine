from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import predict, explain, health

app = FastAPI(
    title="AltScoreMLInferenceAPI",
    description="AlternativecreditscoringMLservice",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(predict.router, prefix="/api/v1", tags=["prediction"])
app.include_router(explain.router, prefix="/api/v1", tags=["explainability"])


@app.get("/")
async def root():
    return {"message": "AltScoreMLService", "status": "operational"}
