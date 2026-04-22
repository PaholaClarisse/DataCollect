from pydantic import BaseModel, Field, EmailStr, ConfigDict, Field, constr, field_validator
from datetime import datetime
from typing import List, Optional, Literal

class ChampFormulaire(BaseModel):
    label: str
    type_champ: Literal[
        "texte",
        "zone_texte",
        "nombre",
        "email",
        "telephone",
        "date",
        "choix_unique",
        "choix_multiple"
    ]
    obligatoire: bool = True
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None

class FormulaireCreate(BaseModel):
    title: str
    description: Optional[str] = None
    champs: List[ChampFormulaire]
    actif: bool = True

class FormulaireUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    champs: Optional[List[ChampFormulaire]] = None
    actif: Optional[bool] = None

class FormulaireResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., alias="_id")
    title: str
    description: Optional[str] = None
    champs: List[ChampFormulaire]
    autor: dict
    actif: bool
    nombre_reponses: int
    created_at: datetime
    updated_at: datetime


class ReponseCreate(BaseModel):
    donnees: dict

class ReponseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., alias="_id")
    formulaire_id: str
    donnees: dict
    created_at: datetime