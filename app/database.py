from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if db_url is None:
    print("LỖI: Không tìm thấy DATABASE_URL. Hãy kiểm tra file .env!")
    exit(1)
# print(f"DEBUG: Giá trị của DATABASE_URL là: '{db_url}'")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# base class cho ORM
Base = declarative_base()

def get_db():
    db = SessionLocal() # Mở một session mới
    try:
        yield db # Cung cấp session cho API sử dụng
    finally:
        db.close()