from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, validator
from sqlmodel import SQLModel, Field

from base import CityEnum


class SessionResponse(SQLModel):
    id: int
    description: Optional[str] = Field(default=None)
    owner: str
    users: List[str]
    city: CityEnum
    district: Optional[str] = Field(default=None)
    facility_name: str
    event_date: datetime
    player_limit: Optional[int] = Field(default=None)
    created_at: datetime

    @validator('users', pre=True)
    def check_users(cls, users):
        return [user.username for user in users]


class SessionResponseForUserResponse(SQLModel):
    id: int
    description: Optional[str] = Field(default=None)
    users: List[str]
    city: CityEnum
    district: Optional[str] = Field(default=None)
    facility_name: str
    event_date: datetime
    player_limit: Optional[int] = Field(default=None)
    created_at: datetime

    @validator('users', pre=True)
    def check_users(cls, users):
        return [user.username for user in users]


class UserResponse(SQLModel):
    id: str
    username: str
    name_and_surname: str
    email: EmailStr
    phone_number: str
    sessions: List[SessionResponseForUserResponse]

    @validator('sessions', pre=True)
    def check_sessions(cls, sessions):
        return [SessionResponseForUserResponse(users=session.users, **session.dict()) for session in sessions]
