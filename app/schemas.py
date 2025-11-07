from pydantic import BaseModel, EmailStr,field_validator, Field
from typing import Optional
import re
from .enum import RoleEnum
# Schema tao user moi 
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=8, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[0-9]{9,15}$')

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
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Loại bỏ khoảng trắng và dấu gạch ngang
        cleaned = re.sub(r'[\s\-]', '', v)
        if not re.match(r'^\+?[0-9]{9,15}$', cleaned):
            raise ValueError('Số điện thoại không hợp lệ')
        return cleaned
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Tên phải có ít nhất 2 ký tự')
        if len(v) > 255:
            raise ValueError('Tên quá dài')
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Tên chỉ được chứa chữ cái và khoảng trắng')
        return v
# Schema tra ve
class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: RoleEnum

    class Config:
        from_attributes = True  # Cho phép đọc từ ORM model
        use_enum_values = True # Tra ve PATIENT that vi enum.PATIENT