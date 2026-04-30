from fastapi import HTTPException, status
from app.schemas.formulaire import FormulaireCreate, FormulaireUpdate, FormulaireResponse, ReponseCreate, ReponseResponse, FormulairePublique
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from bson import ObjectId
from app.database import db
from typing import List, Optional
import csv
import io

class FormulaireService:

    @staticmethod
    async def create_formulaire(formulaire: FormulaireCreate, current_user: dict) -> FormulaireResponse:
        # Logique pour creer un formulaire
        new_formulaire = {
            "title": formulaire.title,
            "description": formulaire.description,
            "champs": [champ.dict() for champ in formulaire.champs],
            "autor": { "id": str(current_user["_id"]), "email": current_user["email"], "name": current_user["name"]},
            "actif": formulaire.actif,
            "nombre_reponses": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # sauvegarder dans la base de donnees et retourner un formulaire cree
        result = await db["formulaires"].insert_one(new_formulaire)
        created_formulaire = await db["formulaires"].find_one({"_id": result.inserted_id})
        created_formulaire["_id"] = str(created_formulaire["_id"])  # Convertir ObjectId en string
        return created_formulaire

    #Lister tous les formulaires (avec pagination et recherche)
    @staticmethod
    async def list_formulaires(skip: int = 0, limit: int = 10, search: Optional[str] = None) ->list:
        query = {}
        if search:
            query["title"] = {"$regex": search, "$options": "i"}  # Recherche insensible à la casse

        cursor = db["formulaires"].find(query).skip(skip).limit(limit)
        formulaires = []
        async for formulaire in cursor:
            formulaire["_id"] = str(formulaire["_id"])  # Convertir ObjectId en string
            formulaires.append(formulaire)
        return formulaires  

    @staticmethod
    async def get_all_formulaires() -> List[FormulaireResponse]:
        cursor = db["formulaires"].find()
        formulaires = []
        async for formulaire in cursor:
            formulaire["_id"] = str(formulaire["_id"])  # Convertir ObjectId en string
            formulaires.append(formulaire)
        return formulaires

    #endpoint pour modifier les informations d'un formulaire
    @staticmethod
    async def update_formulaire(formulaire_id:str, formulaire_update: FormulaireUpdate, current_user: dict) -> FormulaireResponse:
        # logique pour modifier un formulaire
        existing_formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not existing_formulaire:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulaire non trouvé")
        if existing_formulaire["autor"]["id"] != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à modifier ce formulaire")
        update_data = {k: v for k, v in formulaire_update.dict(exclude_unset=True).items()}
        if "champs" in update_data:
            update_data["champs"] = [champ.dict() for champ in formulaire_update.champs]
        update_data["updated_at"] = datetime.utcnow()
        await db["formulaires"].update_one({"_id": ObjectId(formulaire_id)}, {"$set": update_data})
        updated_formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        updated_formulaire["_id"] = str(updated_formulaire["_id"])  # Convertir ObjectId en string
        return updated_formulaire

    #endpoint pour supprimer un formulaire
    @staticmethod
    async def delete_formulaire(formulaire_id: str, current_user:dict):
        existing_formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not existing_formulaire:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="formulaire non trouvé")
        if existing_formulaire["autor"]["id"] != str(current_user["_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à supprimer ce formulaire")
        await db["formulaires"].delete_one({"_id": ObjectId(formulaire_id)})
        return {"message": "Formulaire supprimé avec succès"}

    #endpoint pour recuperer un formulaire public (sans les informations de l'auteur)
    @staticmethod
    async def get_formulaire_public(formulaire_id: str) -> FormulairePublique:
        formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id), "actif": True})
        if not formulaire:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulaire non trouvé ou inactif")
        formulaire["_id"] = str(formulaire["_id"])  # Convertir ObjectId en string
        return formulaire
        
    # endpoints pour la soumission des reponses aux formulaires
    @staticmethod
    async def submit_reponse(formulaire_id: str,reponse: ReponseCreate, current_user: dict) -> dict:
        # 1. Vérifier que le formulaire existe
        formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not formulaire:
            raise HTTPException(status_code=404, detail="Formulaire non trouvé")

        # 2. Vérifier que le formulaire est actif
        if not formulaire["actif"]:
            raise HTTPException(status_code=400, detail="Formulaire inactif")

        # 3. Vérifier que l'user n'a pas déjà soumis
        reponse_existante = await db["reponses"].find_one({"formulaire_id": formulaire_id,"repondant.id": str(current_user["_id"])})
        if reponse_existante:
            raise HTTPException(status_code=400,detail="Vous avez déjà soumis ce formulaire")

        # 4. Vérifier les champs obligatoires
        champs_obligatoires = [champ["label"].strip().lower() for champ in formulaire["champs"] if champ["obligatoire"]]
        donnees_keys = [key.strip().lower() for key in reponse.donnees.keys()]
        for champ in champs_obligatoires:
            if champ not in donnees_keys:
                raise HTTPException(status_code=400, detail=f"Le champ '{champ}' est obligatoire")
        #champs_obligatoires = [champ["label"] for champ in formulaire["champs"] if champ["obligatoire"]]
        #for champ in champs_obligatoires:
            #if champ not in reponse.donnees:
                #raise HTTPException(status_code=400,detail=f"Le champ '{champ}' est obligatoire")

        # 5. Sauvegarder la réponse
        nouvelle_reponse = {
            "formulaire_id": formulaire_id,
            "repondant": {
                "id": str(current_user["_id"]),
                "email": current_user["email"],
                "name": current_user["name"]
            },
            "donnees": reponse.donnees,
            "date_soumission": datetime.utcnow()
        }
        await db["reponses"].insert_one(nouvelle_reponse)

        # 6. Incrémenter nombre_reponses
        await db["formulaires"].update_one({"_id": ObjectId(formulaire_id)},{"$inc": {"nombre_reponses": 1}})

        return {"message": "Réponse soumise avec succès ✅"}

  #consullter les réponses d'un formulaire (seulement pour l'auteur du formulaire)
    @staticmethod
    async def get_reponses(formulaire_id: str, current_user: dict) -> List[ReponseResponse]:
        formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not formulaire:
            raise HTTPException(status_code=404, detail="Formulaire non trouvé")

        #
        #if formulaire["autor"]["id"] != str(current_user["_id"]):
        if str(formulaire.get("autor", {}).get("id")) != str(current_user.get("_id")):
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à consulter les réponses de ce formulaire")
        
        cursor = db["reponses"].find({"formulaire_id":formulaire_id})
        reponses = []
        async for reponse in cursor:
            reponse["_id"] = str(reponse["_id"])  # Convertir ObjectId en string
            reponses.append(reponse)
        return reponses

    #statistique de base sur les réponses d'un formulaire (nombre de réponses, taux de complétion, etc.)
    @staticmethod
    async def get_statistiques(formulaire_id: str, current_user: dict) -> dict :
        formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not formulaire:
            raise HTTPException(status_code=404, detail="Formulaire non trouvé")
        #print(f"autor.id en base: '{formulaire.get('autor', {}).get('id')}'")
        #print(f"current_user._id: '{str(current_user.get('_id'))}'")
        #print(f"sont-ils égaux: {str(formulaire.get('autor', {}).get('id')) == str(current_user.get('_id'))}")
        if str(formulaire.get("autor", {}).get("id")) != str(current_user.get("_id")):
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à consulter les statistiques de ce formulaire")
        
        nombre_reponses = formulaire.get("nombre_reponses", 0)
        # Ici on peut ajouter d'autres statistiques comme le taux de complétion, les réponses par champ, etc.
        
        return {"nombre_reponses": nombre_reponses}

    #endpoind pour exporter les réponses d'un formulaire au format CSV (seulement pour l'auteur du formulaire)
    @staticmethod
    async def export_reponses_csv(formulaire_id: str, current_user: dict) -> str:
        formulaire = await db["formulaires"].find_one({"_id": ObjectId(formulaire_id)})
        if not formulaire:
            raise HTTPException(status_code=404, detail="Formulaire non trouvé")
        if str(formulaire.get("autor", {}).get("id")) != str(current_user.get("_id")):
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à exporter les réponses de ce formulaire")
        
        cursor = db["reponses"].find({"formulaire_id": formulaire_id})
        reponses = []
        async for reponse in cursor:
            reponse["_id"] = str(reponse["_id"])  # Convertir ObjectId en string
            reponses.append(reponse)
        
        # Logique pour convertir les réponses en CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Écrire l'en-tête du CSV
        if reponses:
            header = ["repondant_id", "repondant_email", "repondant_name"] + list(reponses[0]["donnees"].keys()) + ["date_soumission"]
            writer.writerow(header)

            # Écrire les données des réponses
            for reponse in reponses:
                row = [
                    reponse["repondant"]["id"],
                    reponse["repondant"]["email"],
                    reponse["repondant"]["name"]
                ] + list(reponse["donnees"].values()) + [reponse["date_soumission"]]
                writer.writerow(row)

        return output.getvalue()
