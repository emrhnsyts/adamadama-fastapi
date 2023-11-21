from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, SQLModel, select
from starlette import status

from database import engine
from models import User


def get_session():
    with Session(engine) as db_session:
        yield db_session


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='api/v1/users/login')
db_dep = Annotated[Session, Depends(get_session)]

SECRET_KEY = 'emrhnsytsemrhnsytsemrhnsytsemrhnsytsemrhnsytsemrhnsytsemrhnsyts'
ALGORITHM = 'HS256'


class Token(SQLModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == username)).first()

    if user is None or not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dep):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get('id')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        return db.get(User, user_id)

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


user_dependency = Annotated[dict, Depends(get_current_user)]
