# app/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import crud, schemas, database # .. nghĩa là import từ thư mục cha

# 1. Tạo một "Router" mới
# prefix="/users": Tất cả API trong file này sẽ bắt đầu bằng /users
# tags=["Users"]: Gom nhóm API này vào nhóm "Users" trên /docs
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 2. Định nghĩa một Schema tổng hợp cho input
# Vì chúng ta cần tạo cả User và Patient cùng lúc
class UserPatientRegister(BaseModel):
    user_data: schemas.UserCreate
    patient_data: schemas.PatientCreate

# 3. Định nghĩa API Đăng ký
@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user_and_patient(
    register_data: UserPatientRegister, # Nhận dữ liệu tổng hợp
    db: Session = Depends(database.get_db) # Lấy session CSDL
):
    """
    API để đăng ký một tài khoản Bệnh nhân mới.
    Bao gồm thông tin User (đăng nhập) và thông tin Patient (hồ sơ).
    """
    
    # 4. Kiểm tra xem email đã tồn tại chưa
    db_user = crud.get_user_by_email(db, email=register_data.user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký."
        )
    
    # 5. Gọi hàm crud để tạo user VÀ patient
    new_user = crud.create_user(
        db=db, 
        user=register_data.user_data, 
        patient_data=register_data.patient_data
    )
    
    # 6. Trả về thông tin user mới (FastAPI sẽ lọc theo UserOut)
    return new_user