from pydantic import BaseModel, EmailStr, ConfigDict, Field, constr, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)

    @field_validator("password")
    def password_validator(cls, value):
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return value    

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    created_at: datetime

