from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.utils.jwt import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = UserRepository(db).get_by_email(email)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive account")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
