from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas import user_schema
from ..core.secure import CurrentUser, get_current_user
from ..crud import user_crud
from .. import models
from ..database import get_db
from typing import List

# 1. Tạo một "Router" mới
# prefix="/users": Tất cả API trong file này sẽ bắt đầu bằng /users
# tags=["Users"]: Gom nhóm API này vào nhóm "Users" trên /docs
router = APIRouter(
    prefix='/users',
    tags=["Users"]
)



#Dinh nghia API
@router.post("/", response_model=user_schema.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(register_data: user_schema.UserPatientRegister, db: Session = Depends(get_db)):
    try:
        db_user = user_crud.get_user_by_email(db=db, email=register_data.user_data.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email da duoc dang ky!"
        )
        new_user = user_crud.create_user(db=db, user=register_data.user_data, patient_data=register_data.patient_data)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/patients",response_model=List[user_schema.PatientProfileOut], status_code=status.HTTP_200_OK)
async def get_all_patients(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user),skip: int = 0, limit: int = 10):
    try:
        patients = user_crud.get_all_patients(db=db,skip=skip,limit=limit)
        return patients
    except Exception as e: 
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/patient-by-id", response_model=user_schema.PatientProfileOut, status_code=status.HTTP_200_OK)
def get_patient_profile_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        patient = user_crud.get_patient_profile_by_user_id(db=db, user_id=user_id)

        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay ho so benh nhan")
        return patient
    except Exception as e :
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put('/update-patient-profile', response_model=user_schema.PatientProfileOut, status_code=status.HTTP_200_OK)
def update_patient_profile(
    user_id : int,
    patient_update: user_schema.PatientUpdate,
    db: Session = Depends(get_db)    
):
    try:
        update_patient = user_crud.update_patient_profile_by_id(
            db=db,
            user_id=user_id,
            patient_update=patient_update
    )
        if not update_patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay benh nhan")
        return update_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/patient", response_model=user_schema.PatientOut)
def delete_patient_by_id(user_id: int, db: Session = Depends(get_db)):
    try:

        db_patient = user_crud.delete_patient(db=db, user_id=user_id)

        if not db_patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay")
        return db_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

@router.delete("/user", response_model=user_schema.UserOut)
def delete_user_and_patient(user_id : int,db: Session = Depends(get_db)):
    try:
        db_user = user_crud.delete_patient_and_user(db=db, user_id=user_id)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay nguo dung nay")
    
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
