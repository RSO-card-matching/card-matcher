# pylint: disable=no-name-in-module

from typing import Optional

from pydantic import BaseModel



class Sample(BaseModel):
    user_id: int
    card_id: int
    state: str
    wts: bool

class Wish(BaseModel):
    user_id: int
    card_id: int
