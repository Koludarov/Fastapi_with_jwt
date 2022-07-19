from typing import Optional
from uuid import uuid4
import datetime
from fastapi import Depends, HTTPException, status

from src.models.users import users
from src.core.security import encode_password
from src.api.v1.schemas.users import UserCreate, UserModel
from src.api.v1.schemas.users import UserIn
from src.db.db import database
from src.services import ServiceBase
from src.core.security import JWTBearer, decode_access_token, JWTBearer2, decode_refresh_token

__all__ = ("UserService",
           "get_user_service",
           "get_current_user",
           "get_current_user_refresh")


class UserService(ServiceBase):
    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Получить пользователя по id"""
        query = users.select().where(users.c.id == user_id)
        user = await self.database.fetch_one(query=query)
        if user is None:
            return None
        return UserModel.parse_obj(user)

    async def get_by_uuid(self, uuid: str) -> Optional[UserModel]:
        """Получить пользователя по uuid"""
        query = users.select().where(users.c.uuid == uuid)
        user = await self.database.fetch_one(query=query)
        if user is None:
            return None
        return UserModel.parse_obj(user)

    async def create_user(self, u: UserCreate):
        """Создаём пользователя и записываем в БД"""
        query1 = users.select().where(users.c.username == u.username)
        user1 = await self.database.fetch_one(query=query1)
        query2 = users.select().where(users.c.email == u.email)
        user2 = await self.database.fetch_one(query=query2)
        if user1 is None and user2 is None:
            user = UserModel(
                uuid=str(uuid4()),
                username=u.username,
                email=u.email,
                password=encode_password(u.password),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            values = {**user.dict()}
            values.pop('id', None)
            query = users.insert().values(**values)
            user.id = await self.database.execute(query)
            return user
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Username or email already exists')

    async def update(self, password: str, uuid: str,
                     user_id: int, u: UserIn) -> UserModel:
        """Обновляем информацию о пользователе и записываем в БД"""
        user = UserModel(
            id=user_id,
            password=password,
            uuid=uuid,
            username=u.username,
            email=u.email,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        values = {**user.dict()}
        values.pop('created_at', None)
        values.pop('id', None)
        query = users.update().where(users.c.id == user_id).values(**values)
        await self.database.execute(query)
        return user

    async def get_by_name(self, name: str) -> Optional[UserModel]:
        """Получить пользователя по username"""
        query = users.select().where(users.c.username == name)
        user = await self.database.fetch_one(query=query)
        if user is None:
            return None
        return UserModel.parse_obj(user)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Получить пользователя по email"""
        query = users.select().where(users.c.email == email)
        user = await self.database.fetch_one(query=query)
        if user is None:
            return None
        return UserModel.parse_obj(user)


def get_user_service() -> UserService:
    return UserService(database)


async def get_current_user(
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(JWTBearer())
) -> UserModel:
    cred_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                   detail='Credentials are not valid')
    payload = decode_access_token(token)
    if payload is None:
        raise cred_exception
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise cred_exception
    user = await user_service.get_by_id(user_id=user_id)
    if user is None:
        raise cred_exception
    return user


async def get_current_user_refresh(
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(JWTBearer2())
) -> UserModel:
    cred_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                   detail='Credentials are not valid')
    payload = decode_refresh_token(token)
    if payload is None:
        raise cred_exception
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise cred_exception
    user = await user_service.get_by_id(user_id=user_id)
    if user is None:
        raise cred_exception
    return user
