# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from . import models               # <-- 1. IMPORT MODELS
from .database import engine, Base, get_db      # <-- 2. IMPORT ENGINE
# from .routers import user_router
from . import models, schemas, crud
from sqlalchemy.orm import Session

# --- 3. TẠO BẢNG TRONG CSDL ---
# Dòng này sẽ kiểm tra CSDL của bạn (qua 'engine')
# và tạo bất kỳ bảng nào (từ 'models') chưa tồn tại.
models.Base.metadata.create_all(bind=engine)
# --------------------------------

app = FastAPI(
    title="Medical Booking API",
    description="API cho hệ thống đặt lịch khám bệnh",
    version="1.0.0"
)

# (Các API router sẽ được thêm vào đây sau)
# --- 2. "MÓC" ROUTER VÀO ỨNG DỤNG ---
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)
@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API Đặt lịch Khám bệnh!"}