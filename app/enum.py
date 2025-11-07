import enum
from sqlalchemy import Enum

class RoleEnum(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"