from sqlalchemy.orm import Session, joinedload
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

def create_user(db: Session, user: schemas.UserCreate, patient_data: schemas.PatientCreate):
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=get_password_hash(password=user.password),
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.flush()

    db_patient = models.Patient(
        user_id=db_user.user_id,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        address=patient_data.date_of_birth
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_patient_profile_by_user_id(db: Session, user_id: int):
    return db.query(models.Patient).options(
        joinedload(models.Patient.user)
    ).filter(models.Patient.user_id == user_id).first()

def get_all_patients(db: Session, skip: int = 0, limit: int = 10):

    return db.query(models.Patient).options(
        joinedload(models.Patient.user)
    ).offset(skip).limit(limit).all()

def update_patient_profile_by_id(db: Session, user_id: int, patient_update: schemas.PatientUpdate):

    db_patient = db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

    if not db_patient:
        return None
    
    update_data = patient_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(db_patient, key):
            setattr(db_patient, key, value)
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    return get_patient_profile_by_user_id(db=db,user_id=user_id)

def delete_patient(db: Session, user_id: int):
    db_patient = db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

    if not db_patient:
        return None
    
    db.delete(db_patient)
    db.commit()

    return db_patient

def delete_patient_and_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()

    return db_user