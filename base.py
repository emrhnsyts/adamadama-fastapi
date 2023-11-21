from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import validator, EmailStr
from sqlmodel import SQLModel, Field


class CityEnum(Enum):
    TRABZON = 'TRABZON'
    ISTANBUL = 'ISTANBUL'
    IZMIR = 'IZMIR'
    ANKARA = 'ANKARA'


class SessionBase(SQLModel):
    description: Optional[str] = Field(default=None, min_length=2, max_length=255)
    city: CityEnum
    district: Optional[str] = Field(default=None, min_length=2, max_length=255)
    facility_name: str = Field(min_length=2, max_length=30)
    event_date: datetime
    player_limit: Optional[int] = Field(default=None, ge=2, le=22)

    @validator('event_date')
    def check_event_date(cls, event_date):
        if datetime(event_date.year, event_date.month, event_date.day,
                    event_date.hour, event_date.minute,
                    event_date.second) < datetime.now():
            raise ValueError("Event date can not be past.")
        return event_date


class UserBase(SQLModel):
    username: str = Field(unique=True, min_length=2, max_length=20)
    email: EmailStr = Field(unique=True)
    phone_number: str = Field(unique=True, min_length=8, max_length=12)
    name: str = Field(min_length=2, max_length=30)
    surname: str = Field(min_length=2, max_length=30)
    password: str = Field(min_length=5)
