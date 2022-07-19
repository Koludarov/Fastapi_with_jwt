from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class Login(BaseModel):
    email: EmailStr
    password: str


class Login2(BaseModel):
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "your_username",
                "password": "your_password"
            }
        }
