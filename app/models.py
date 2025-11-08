# app/models.py
from sqlalchemy import (
    Column, Integer, String, Enum, ForeignKey, 
    DATETIME, BOOLEAN, TEXT, DATE
)
import enum
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base  # Import Base từ file database.py
from .enum import RoleEnum, GenderEnum
#-------------
# 0. Role enum 
#-------------


# ----------------------------------------------
# 1. Bảng Users (Đa vai trò)
# ----------------------------------------------
class User(Base):
    __tablename__ = "Users"  # Tên bảng trong MySQL

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.PATIENT, nullable=False)

    # Định nghĩa các mối quan hệ (links)
    # uselist=False vì đây là quan hệ 1-1 (1 User chỉ có 1 hồ sơ Doctor)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    patient_profile = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")

    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)
# ----------------------------------------------
# 2. Bảng Specialties (Chuyên khoa)
# ----------------------------------------------
class Specialty(Base):
    __tablename__ = "Specialties"

    specialty_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(TEXT, nullable=True)

    # Quan hệ 1-Nhiều: 1 Chuyên khoa có nhiều bác sĩ
    doctors = relationship("Doctor", back_populates="specialty")
    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)
# ----------------------------------------------
# 3. Bảng Doctors (Hồ sơ Bác sĩ)
# ----------------------------------------------
class Doctor(Base):
    __tablename__ = "Doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    # Khóa ngoại liên kết 1-1 với bảng Users
    user_id = Column(Integer, ForeignKey("Users.user_id"), unique=True, nullable=False)
    # Khóa ngoại liên kết với bảng Specialties
    specialty_id = Column(Integer, ForeignKey("Specialties.specialty_id"), nullable=True)
    
    bio = Column(TEXT, nullable=True)
    clinic_address = Column(String(255), nullable=True)

    # Mối quan hệ ngược lại (để truy cập từ Doctor -> User)
    user = relationship("User", back_populates="doctor_profile")
    # Mối quan hệ ngược lại (để truy cập từ Doctor -> Specialty)
    specialty = relationship("Specialty", back_populates="doctors")
    
    # Quan hệ 1-Nhiều: 1 Bác sĩ có nhiều lịch làm việc
    availabilities = relationship("Availability", back_populates="doctor")
    # Quan hệ 1-Nhiều: 1 Bác sĩ có nhiều lịch hẹn
    appointments = relationship("Appointment", back_populates="doctor")
    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)
# ----------------------------------------------
# 4. Bảng Patients (Hồ sơ Bệnh nhân)
# ----------------------------------------------
class Patient(Base):
    __tablename__ = "Patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    # Khóa ngoại liên kết 1-1 với bảng Users
    user_id = Column(Integer, ForeignKey("Users.user_id"), unique=True, nullable=False)
    
    date_of_birth = Column(DATE, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    address = Column(TEXT, nullable=True)

    # Mối quan hệ ngược lại
    user = relationship("User", back_populates="patient_profile")
    
    # Quan hệ 1-Nhiều: 1 Bệnh nhân có nhiều lịch hẹn
    appointments = relationship("Appointment", back_populates="patient")
    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)
# ----------------------------------------------
# 5. Bảng Availability (Lịch làm việc)
# ----------------------------------------------
class Availability(Base):
    __tablename__ = "Availability"

    availability_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("Doctors.doctor_id"), nullable=False, index=True)
    start_time = Column(DATETIME, nullable=False)
    end_time = Column(DATETIME, nullable=False)
    is_booked = Column(BOOLEAN, nullable=False, default=False)

    # Mối quan hệ ngược lại
    doctor = relationship("Doctor", back_populates="availabilities")
    
    # Quan hệ 1-1: 1 slot lịch chỉ thuộc 1 appointment
    appointment = relationship("Appointment", back_populates="availability_slot", uselist=False)
    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)
# ----------------------------------------------
# 6. Bảng Appointments (Lịch hẹn)
# ----------------------------------------------
class Appointment(Base):
    __tablename__ = "Appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("Patients.patient_id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("Doctors.doctor_id"), nullable=False, index=True)
    # Khóa ngoại 1-1, đảm bảo slot này không bị đặt 2 lần
    availability_id = Column(Integer, ForeignKey("Availability.availability_id"), unique=True, nullable=False)
    
    reason_for_visit = Column(TEXT, nullable=True)
    status = Column(Enum('SCHEDULED', 'COMPLETED', 'CANCELED_PATIENT', 'CANCELED_DOCTOR'), nullable=False)

    # Mối quan hệ ngược lại
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    availability_slot = relationship("Availability", back_populates="appointment")
    created_at = Column(DATETIME, default=datetime.utcnow, nullable=False)
    updated_at = Column(DATETIME, default=datetime.utcnow, onupdate=datetime.utcnow)