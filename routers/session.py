from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from starlette import status
from datetime import datetime

from dependencies import user_dependency, db_dep
from models import Session
from requests import SessionCreateRequest
from responses import SessionResponse

router = APIRouter(
    prefix='/api/v1/sessions',
    tags=['sessions']
)


@router.get('/')
def get_sessions(db: db_dep, limit: Annotated[int, Query(ge=10, le=10)] = 10, offset:int=0):
    sessions = db.exec(select(Session).limit(limit).offset(offset)).all()
    return [SessionResponse(
        owner=session.owner.username,
        users=session.users,
        **session.dict()
    ) for session in sessions]


@router.post('/')
def add_session(user: user_dependency, db: db_dep, session_create_request: SessionCreateRequest):
    session_db = Session(**session_create_request.dict())
    session_db.owner_id = user.id
    session_db.users.append(user)
    db.add(session_db)
    db.commit()


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(user: user_dependency, db: db_dep, session_id: int):
    session_to_be_deleted = db.get(Session, session_id)
    if session_to_be_deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found.')

    elif user.id != session_to_be_deleted.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is not the owner of this session.')

    db.delete(session_to_be_deleted)
    db.commit()


@router.put('/{session_id}')
def leave_session(user: user_dependency, db: db_dep, session_id: int):
    session_to_be_updated = db.get(Session, session_id)
    if session_to_be_updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found.')

    elif session_to_be_updated.owner_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User can not be removed from his/her own session.')

    elif user not in session_to_be_updated.users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User is not in the session.')
    session_to_be_updated.users.remove(user)
    db.add(session_to_be_updated)
    db.commit()


@router.post('/{session_id}', status_code=status.HTTP_201_CREATED)
def join_session(user: user_dependency, db: db_dep, session_id: int):
    session_to_be_updated = db.get(Session, session_id)
    if session_to_be_updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found.')

    elif datetime.now() > session_to_be_updated.event_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Can not join the session as it has passed.")

    elif user in session_to_be_updated.users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User is already in the session.")

    elif session_to_be_updated.player_limit is not None and len(
            session_to_be_updated.users) >= session_to_be_updated.player_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Player limit exceeds.")
    session_to_be_updated.users.append(user)
    db.add(session_to_be_updated)
    db.commit()
