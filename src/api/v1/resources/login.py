from fastapi import APIRouter, Depends, HTTPException, status
from src.api.v1.schemas.token import Token, Login2
from src.services.user import UserService, get_user_service
from src.core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token
from src.services.reshresh_token import RefreshService, get_refresh_service

router = APIRouter()


@router.post('/', summary="Вход в систему",
             tags=["user"], response_model=Token)
async def login(log_in: Login2,
                users: UserService = Depends(get_user_service),
                refresh_service: RefreshService = Depends(get_refresh_service)):
    user = await users.get_by_name(log_in.username)
    if user is None or not verify_password(log_in.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
    refresh_token = create_refresh_token(data={"user_id": user.id,
                                               "user_uuid": user.uuid})
    refresh_service.save_token(user_id=user.id, token=refresh_token)
    ref_id = decode_refresh_token(refresh_token).get('jti')
    access_token = create_access_token(data={"username": user.username,
                                             "email": user.email,
                                             "user_uuid": user.uuid,
                                             "refresh_uuid": ref_id,
                                             "user_id": user.id,
                                             "is_superuser": user.is_superuser,
                                             "created_at": str(user.created_at),
                                             "roles": user.roles})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )
