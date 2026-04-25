from fastapi import APIRouter, Depends, status, HTTPException
from app.services.auth import get_current_user
from app.services.formulaires import FormulaireService
from app.schemas.formulaire import FormulaireCreate, FormulaireResponse, FormulaireUpdate, FormulairePublique, ReponseCreate, ReponseResponse


router = APIRouter()

@router.post("/formulaires", status_code=status.HTTP_201_CREATED)
async def create_formulaire(formulaire: FormulaireCreate, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.create_formulaire(formulaire, current_user)

@router.get("/formulaires")
async def list_formulaires(skip: int = 0, limit: int = 10, search: str = None):
    return await FormulaireService.list_formulaires(skip=skip, limit=limit, search=search)

@router.get("/formulaires/all")
async def get_all_formulaires():
    return await FormulaireService.get_all_formulaires()

@router.put("/formulaires/{formulaire_id}")
async def update_formulaire(formulaire_id: str, formulaire_update: FormulaireUpdate, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.update_formulaire(formulaire_id, formulaire_update, current_user)

@router.delete("/formulaires/{formulaire_id}", status_code=status.HTTP_200_OK)
async def delete_formulaire(formulaire_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    return await FormulaireService.delete_formulaire(formulaire_id, current_user)

#recuperer un formulaire public (sans les informations de l'auteur)
@router.get("/formulaires/{formulaire_id}/public")
async def get_formulaire_public(formulaire_id: str):
    return await FormulaireService.get_formulaire_public(formulaire_id)

#endpoint pour soumettre une reponse a un formulaire
@router.post("/formulaires/{formulaire_id}/reponses", status_code=status.HTTP_201_CREATED)
async def submit_reponse(formulaire_id: str, reponse: ReponseCreate, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.submit_reponse(formulaire_id, reponse, current_user)

#endpoint pour recuperer les reponses d'un formulaire (seulement pour l'auteur du formulaire)
@router.get("/formulaires/{formulaire_id}/reponses")
async def get_reponses(formulaire_id: str, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.get_reponses(formulaire_id, current_user)

#endpoint pour connaitre les statistique d'un formulaire (nombre de reponses)
@router.get("/formulaires/{formulaire_id}/statistiques")
async def get_statistiques(formulaire_id: str, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.get_statistiques(formulaire_id, current_user)

#endpoint pour exporter les reponses d'un formulaire au format csv
@router.get("/formulaires/{formulaire_id}/export")
async def export_reponses_csv(formulaire_id: str, current_user: dict = Depends(get_current_user)):
    return await FormulaireService.export_reponses_csv(formulaire_id, current_user)

