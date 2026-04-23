from fastapi import HTTPException, status
from app.database import db
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate
from app.services.auth import hash_password, verify_password, create_access_token
from datetime import datetime

class AuthService:

    @staticmethod
    async def signup(user: UserCreate):
        # 1. Vérifier si email existe
        existing_user = await db["users"].find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )

        # 2. Hacher le mot de passe
        hashed_pwd = hash_password(user.password)

        # 3. Préparer le document
        new_user = {
            "name": user.name,
            "email": user.email,
            "password": hashed_pwd,
            "created_at": datetime.utcnow()
        }

        # 4. Insérer dans MongoDB
        result = await db["users"].insert_one(new_user)

        return {
            "message": "Utilisateur créé avec succès",
            "user_id": str(result.inserted_id)
        }

    @staticmethod
    async def login(form_data):
        # 1. Vérifier si l'utilisateur existe
        db_user = await db["users"].find_one({"email": form_data.username})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email incorrect"
            )

        # 2. Vérifier le mot de passe
        if not verify_password(form_data.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe incorrect"
            )

        # 3. Créer le token JWT
        access_token = create_access_token(data={
            "sub": db_user["email"],
            "user_id": str(db_user["_id"])
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }