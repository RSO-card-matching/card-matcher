# pylint: disable=no-name-in-module

from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, String


Base = declarative_base()


class Sample(BaseModel):
    user_id: int
    card_id: int
    state: str
    wts: bool

class Wish(BaseModel):
    user_id: int
    card_id: int
