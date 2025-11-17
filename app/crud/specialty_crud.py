from sqlalchemy.orm import Session

from .. import models
from ..schemas import specialty_schema
def create_specialty(db: Session, specialty: specialty_schema.SpecialtyCreate):
    try:
        db_specialty = models.Specialty(
            name = specialty.name,
            description = specialty.description
        )

        db.add(db_specialty)
        db.commit()
        db.refresh(db_specialty)
        return db_specialty
    except Exception as e:
        db.rollback()
        print(str(e))
        return None
    
def get_all_specialties(db: Session, skip: int = 0, limit: int =10):
    return db.query(models.Specialty).offset(skip).limit(limit).all()

def get_specialty_by_id(db: Session, specialty_id: int):
    return db.query(models.Specialty).filter(models.Specialty.specialty_id == specialty_id).first()
def get_specialty_by_name(db: Session, name: str):
    return db.query(models.Specialty).filter(models.Specialty.name == name).first()

def update_specialty(db: Session, specialty_id: int, specialty_update: specialty_schema.SpecialtyCreate):

    db_specialty = db.query(models.Specialty).filter(models.Specialty.specialty_id == specialty_id).first()

    if not db_specialty:
        return None
    update_data = specialty_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(db_specialty, key):
            setattr(db_specialty, key,value)

    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)

    return get_specialty_by_id(db=db, specialty_id=specialty_id)

def delete_specialty(db: Session, specialty_id: int):
    db_specialty = db.query(models.Specialty).filter(models.Specialty.specialty_id == specialty_id).first()

    if not db_specialty: 
        return None
    
    db.delete(db_specialty)
    db.commit()

    return db_specialty