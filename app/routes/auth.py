from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import get_current_user, create_access_token, verify_password, hash_password
from app.database import db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from fastapi import APIRouter

router = APIRouter()

#verification de l'authentification de l'utilisateur
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    existing_user =  await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")
    
    hashed_pwd = hash_password(user.password)
    
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pwd
    }
    result = await db["users"].insert_one(new_user)
    return {"message": "Utilisateur créé avec succès", "user_id": str(result.inserted_id)}

#verification de l'authentification de l'utilisateur et création du token JWT pour les utilisateurs qui se connecten
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    #  Vérifier si l'utilisateur existe
    db_user = await db["users"].find_one({"email": form_data.username})
        
    if not db_user:
        raise HTTPException(status_code=401, detail="Email incorrect")
    
    #  Vérifier le mot de passe
    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    
    # Créer le JWT
    access_token = create_access_token(data={"sub": db_user["email"], "user_id": db_user["_id"]})
    
    # Retourner le token
    return {"access_token": access_token, "token_type": "bearer"}