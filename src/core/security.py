import redis
from jose import jwt
from uuid import uuid4
from passlib.context import CryptContext
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.reshresh_token import RefreshService, get_refresh_service
from src.services.access_token import AccessService, get_access_service
from src.core.config import JWT_ALGORITHM, JWT_SECRET_KEY, REDIS_PORT, REDIS_HOST
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

hasher = CryptContext(schemes=['bcrypt'], deprecated="auto")


def encode_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return hasher.verify(password, encoded)


blocked_access_tokens = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True,
)
active_refresh_tokens = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=2, decode_responses=True,
)


def create_access_token(data: dict) -> str:
    to_encode = {
        'fresh': 'true',
        'iat': datetime.utcnow(),
        'type': 'access',
        'jti': str(uuid4()),
        'nbf': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )}
    to_encode.update(data)
    return jwt.encode(to_encode, JWT_SECRET_KEY,
                      algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = {
        'fresh': 'true',
        'iat': datetime.utcnow(),
        'type': 'refresh',
        'jti': str(uuid4())}
    to_encode.update(data)
    to_encode.update({
        'nbf': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )})
    return jwt.encode(to_encode, JWT_SECRET_KEY,
                      algorithm=JWT_ALGORITHM)


def decode_access_token(token: str):
    try:
        encoded_jwt = jwt.decode(token, JWT_SECRET_KEY,
                                 algorithms=JWT_ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token expired')
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    return encoded_jwt


def decode_refresh_token(token: str):
    try:
        encoded_jwt = jwt.decode(token, JWT_SECRET_KEY,
                                 algorithms=JWT_ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token expired')
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    return encoded_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request,
                       access_service: AccessService = Depends(get_access_service), ):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        exp = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid access token')
        if credentials:
            access_token = decode_access_token(credentials.credentials)
            if access_token is None:
                raise exp
            blocked_token = access_service.get_token(access_token.get('jti'))
            if blocked_token:
                raise exp
            return credentials.credentials
        else:
            raise exp


class JWTBearer2(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer2, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request,
                       refresh_service: RefreshService = Depends(get_refresh_service)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer2, self).__call__(request)
        exp = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid refresh token')
        if credentials:
            refresh_token = decode_refresh_token(credentials.credentials)
            if refresh_token is None:
                raise exp
            active_token = refresh_token.get('jti')
            user_id = refresh_token.get('user_id')
            if not refresh_service.check_refresh_token(user_id=user_id,
                                                       token=active_token):
                raise exp
            return credentials.credentials
        else:
            raise exp
