from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv('SECRET')
salt = bcrypt.gensalt()
def get_password_hash(password: str) -> str:
    hash_password = bcrypt.hashpw(password=password.encode('utf-8'), salt=salt)
    return hash_password.decode('utf-8')

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=get_password_hash(password=user.password),
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user