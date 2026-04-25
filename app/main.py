from fastapi import FastAPI, Depends, HTTPException, status
from app.routes import auth, formulaires
from app.database import settings
from bson import ObjectId
from fastapi.encoders import ENCODERS_BY_TYPE

ENCODERS_BY_TYPE[ObjectId] = str  # Convertir ObjectId en string lors de la sérialisation

app = FastAPI(title="API de Collecte de Données", description="Une API pour la collecte de données avec authentification JWT", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de Collecte de Données!"}
    
app.include_router(auth.router)
app.include_router(formulaires.router)