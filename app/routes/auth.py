from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import get_current_user, create_access_token, verify_password, hash_password
from app.services.authent import AuthService
from app.database import db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from fastapi import APIRouter

router = APIRouter()

#verification de l'authentification de l'utilisateur
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    return await AuthService.signup(user)
    
#route pour la connexion de l'utilisateur
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await AuthService.login(form_data)