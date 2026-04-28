from fastapi import FastAPI, Depends, HTTPException, status
from app.routes import auth, formulaires
from app.database import settings
from bson import ObjectId
from fastapi.encoders import ENCODERS_BY_TYPE
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

ENCODERS_BY_TYPE[ObjectId] = str  # Convertir ObjectId en string lors de la sérialisation

app = FastAPI(title="API de Collecte de Données", description="Une API pour la collecte de données avec authentification JWT", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

'''@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de Collecte de Données!"}'''
    
app.include_router(auth.router)
app.include_router(formulaires.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html",{"request": request})

@app.get("/f/{formulaire_id}", response_class=HTMLResponse)
async def formulaire_public(request: Request, formulaire_id: str):
    return templates.TemplateResponse("formulaire_public.html",{"request": request, "formulaire_id": formulaire_id})

@app.get("/formulaires/{formulaire_id}/reponses", response_class=HTMLResponse)
async def voir_reponses(request: Request, formulaire_id: str):
    return templates.TemplateResponse("voir_reponses.html", {"request": request, "formulaire_id": formulaire_id})

@app.get("/api/formulaires/{formulaire_id}/export", response_class=HTMLResponse)
async def exporter_responses(request:Request, formulaire_id: str):
    return templates.TemplateResponse("voir_reponses.html", {"request": request, "formulaire_id": formulaire_id})