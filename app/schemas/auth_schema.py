from pydantic import BaseModel, EmailStr,field_validator, Field # type: ignore
from typing import Optional
from datetime import date
import re

class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    @field_validator('password')
    @classmethod
    def validate_password(cls, v): 
        if not any(char.isdigit() for char in v):
            raise ValueError('Password phải chứa ít nhất 1 số')
        if not any(char.isupper() for char in v):
            raise ValueError('Password phai chua it nhat mot chu hoa')
        if not any(char.islower() for char in v):
            raise ValueError('Password phai chua it nhat mot chu thuong')
        return v

