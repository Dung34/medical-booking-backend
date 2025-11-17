from fastapi import APIRouter,status, HTTPException, Depends, Response, Request
from ..schemas.user_schema import UserOut
from ..schemas.auth_schema import LoginSchema
from ..crud.user_crud import get_user_by_email, get_password_hash, get_user_by_id
from sqlalchemy.orm import Session 
from ..database import get_db
from ..core.secure import create_access_token, create_refresh_token, verify_password, verify_refresh_token
router = APIRouter(
    prefix='/auth',
    tags=["Auth"]
)

@router.post("/login", status_code=status.HTTP_200_OK)
def login(response: Response,login_data: LoginSchema, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db=db, email=login_data.email)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Người dùng email này không tồn tại!")
       

        if not verify_password(login_data.password, db_user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        
        access_token = create_access_token(data={
            "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id),
            "full_name": db_user.full_name,
            "email" : db_user.email,
            "role" : db_user.role
        })
        refresh_token = create_refresh_token(data={
            "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id)
        })

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            secure=True,
            max_age=7*24*60*60,
            path="/"
        )
        
        return {
        "access_token": access_token,
        "refresh_token" : refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": db_user.user_id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role
        }
    }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))        
    

@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Không tìm thấy refresh token")
    try:
        payload = verify_refresh_token(refresh_token)
        user_id = int(payload.get("sub"))
        if not user_id :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Refresh khong hop le")
        db_user = get_user_by_id(db=db, user_id=user_id)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nguoi dung khong ton tai")
        
        new_access_token = create_access_token(data={ 
            "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id),
            "full_name": db_user.full_name,
            "email" : db_user.email,
            "role" : db_user.role})
        new_refresh_token = create_refresh_token(data={
            "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id)
        })
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            samesite="strict",
            secure=True,
            max_age=7*24*60*60,
            path="/"
        )
        return {
            "access_token": new_access_token,
        "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


        

@router.post("/manual-refresh",status_code=status.HTTP_200_OK)
def refresh_token_manual(refresh_token : str, db: Session = Depends(get_db)):
    try:
        payload = verify_refresh_token(refresh_token)
        user_id = int(payload.get("sub"))
        if not user_id : 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token khong hop le")
        db_user = get_user_by_id(db=db, user_id=user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nguoi dung nay khong ton tai")
        new_access_token = create_access_token(data={ "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id),
            "full_name": db_user.full_name,
            "email" : db_user.email,
            "role" : db_user.role})
        new_refresh_token = create_refresh_token(data={
            "sub": str(db_user.user_id),
            "user_id": str(db_user.user_id)
        })
        return{
             "access_token": new_access_token,
             "refresh_token" : new_refresh_token,
        "token_type": "bearer",
        } 
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
