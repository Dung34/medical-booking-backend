from pydantic import BaseModel, EmailStr,field_validator, Field # type: ignore
from typing import Optional
from datetime import date

class SpecialtyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)

class SpecialtyOut(BaseModel):
    name: str
    specialty_id: int
    description: str
