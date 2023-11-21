from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from base import SessionBase, UserBase


class SessionUserLink(SQLModel, table=True):
    user_id: Optional[int] = Field(
        foreign_key="user.id", primary_key=True
    )
    session_id: Optional[int] = Field(
        foreign_key="session.id", primary_key=True
    )


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    sessions: List['Session'] = Relationship(back_populates="users", link_model=SessionUserLink)
    owned_sessions: List["Session"] = Relationship(back_populates="owner")


class Session(SessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default=datetime.now())

    owner_id: int = Field(foreign_key='user.id')

    users: List[User] = Relationship(back_populates="sessions", link_model=SessionUserLink)
    owner: User = Relationship(back_populates="owned_sessions")
