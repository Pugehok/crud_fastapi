import datetime as _dt

import pydantic as _pydantic


class Token(_pydantic.BaseModel):
    access_token: str
    token_type: str



class _UserBase(_pydantic.BaseModel):
    email: str


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        from_attributes = True


class User(_UserBase):
    id: int

    class Config:
        from_attributes = True


class _LeadBase(_pydantic.BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str


class LeadCreate(_LeadBase):
    pass


class Lead(_LeadBase):
    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        from_attributes = True

