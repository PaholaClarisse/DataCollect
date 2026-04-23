from fastapi import FastAPI, Depends, HTTPException, status
from app.routes import auth
from app.database import settings

app = FastAPI(title="API de Collecte de Données", description="Une API pour la collecte de données avec authentification JWT", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de Collecte de Données!"}
    
app.include_router(auth.router)