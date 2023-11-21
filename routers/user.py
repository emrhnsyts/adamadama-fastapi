from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette import status

from dependencies import bcrypt_context, authenticate_user, create_access_token, db_dep
from models import User
from requests import UserCreateRequest
from responses import UserResponse

router = APIRouter(
    prefix='/api/v1/users',
    tags=['users']
)


@router.get('/{username}')
def get_user_by_username(username: str, db: db_dep):
    user = db.exec(select(User).where(User.username == username)).first()
    if user is not None:
        return UserResponse(
            name_and_surname=user.name + " " + user.surname,
            sessions=user.owned_sessions,
            **user.dict()
        )
    else:
        raise HTTPException(status_code=404, detail='user not found.')


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(db: db_dep, user_create_request: UserCreateRequest):
    try:
        db_user = User(
            username=user_create_request.username,
            name=user_create_request.name,
            surname=user_create_request.surname,
            email=user_create_request.email,
            password=bcrypt_context.hash(user_create_request.password),
            phone_number=user_create_request.phone_number
        )
        db.add(db_user)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists.')


@router.post('/login')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dep):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}
