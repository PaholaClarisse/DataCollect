from argon2 import  PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from jose.exceptions import JWTError
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from app.database import db
from app.configure import settings
from fastapi import HTTPException, status, Depends

argon2 = PasswordHasher()

#fonction pour hacher le mot de passe
def hash_password(password:str ) -> str:
    #convertir le mot de passe en bytes et le tronquer à 72 caractères pour éviter les problèmes avec argon2
    password = password.encode("utf-8")[:72]
    #reconvertir le mot de passe haché en string pour le stocker dans la base de données
    password = password.decode("utf-8", "ignore")
    #returner le mot de passe haché
    return argon2.hash(password)

#foncton pour vérifier le mot de passe
def verify_password(plain_password:str, hashed_password:str) -> bool:
    try:
        return argon2.verify(plain_password, hashed_password)
    except Exception:
        return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# fonction pour obtenir l'utilisateur actuel à partir du token JWT
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token d'authentification invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db["users"].find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

# fonction pour créer un token JWT
async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt  