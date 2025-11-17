from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import specialty_schema
from ..crud import specialty_crud
from typing import List
from ..database import get_db
router = APIRouter(
    prefix="/specialties",
    tags=["Specialties"]
)

@router.post("/", response_model= specialty_schema.SpecialtyOut, status_code=status.HTTP_201_CREATED)
def create_specialty(specialty_data: specialty_schema.SpecialtyCreate, db: Session = Depends(get_db)):
    try:
        db_specialty = specialty_crud.get_specialty_by_name(db=db, name=specialty_data.name)

        if db_specialty:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chuyen khoa nay da ton tai roi")
        new_specialty = specialty_crud.create_specialty(db=db, specialty=specialty_data)
        return new_specialty
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.get("/", response_model=List[specialty_schema.SpecialtyOut], status_code= status.HTTP_200_OK)
def get_specialties(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    try:
        specialties = specialty_crud.get_all_specialties(db=db,skip=skip, limit=limit)
        return specialties
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.get("/{specialty_id}", response_model=specialty_schema.SpecialtyOut)
def get_specialty_by_id(specialty_id : int,db: Session = Depends(get_db)):
    try: 
        db_specialty = specialty_crud.get_specialty_by_id(db=db, specialty_id=specialty_id)
        if not db_specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chuyen khoa khong ton tai"
            )
        return db_specialty
    except Exception as e :
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.put("/{specialty_id}", response_model=specialty_schema.SpecialtyOut, status_code=status.HTTP_200_OK)
def update_specialty(
    specialty_id: int,
    specialty_update: specialty_schema.SpecialtyCreate,
    db: Session = Depends(get_db)
):
    try:
        update_specialty = specialty_crud.update_specialty(
            db=db,
            specialty_id=specialty_id,
            specialty_update=specialty_update
        )
        if not update_specialty:
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail="Chuyen khoa nay khong ton tai"
             )
        return update_specialty
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{specialty_id}", response_model= specialty_schema.SpecialtyOut, status_code=status.HTTP_200_OK)
def delete_specialty(
    specialty_id: int,
    db: Session = Depends(get_db)
):
    try:
        db_specialty = specialty_crud.delete_specialty(
            db=db,
            specialty_id=specialty_id
        )
        if not db_specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chuyen nganh nay khong ton tai"
            )
        return db_specialty
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
