from datetime import datetime
from pydantic import BaseModel, EmailStr


__all__ = (
    "UserBase",
    "UserCreate",
    "UserModel",
    "UserIn",
    "UserOut",
    "YourModel"
)


class UserIn(BaseModel):
    username: str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "username": "your_username",
                "email": "user@example.com",
            }
        }


class UserBase(UserIn):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "your_username",
                "email": "user@example.com",
                "password": "your_password"
            }
        }


class UserCreate(UserBase):
    ...


class UserModel(BaseModel):
    id: int = None
    username: str
    email: EmailStr
    password: str
    roles: str = '[]'
    created_at: datetime
    is_superuser: bool = False
    uuid: str
    is_totp_enabled: bool = False
    is_active: bool = True


class UserOut(BaseModel):
    id: int = None
    username: str
    email: EmailStr
    roles: str = '[]'
    created_at: datetime
    is_superuser: bool = False
    uuid: str
    is_totp_enabled: bool = False
    is_active: bool = True


class YourModel(BaseModel):
    msg: str = "Update is successful. Please use new access token"
    user: UserOut
    access_token: str
