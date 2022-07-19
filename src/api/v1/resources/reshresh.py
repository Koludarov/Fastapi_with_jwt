from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.schemas.token import Token
from src.api.v1.schemas.users import UserModel
from src.services.user import UserService, get_user_service, get_current_user_refresh
from src.core.security import create_access_token, create_refresh_token
from src.core.security import decode_refresh_token, JWTBearer
from src.services.reshresh_token import RefreshService, get_refresh_service
from src.services.access_token import AccessService, get_access_service

router = APIRouter()


@router.post('/', summary="Обновляем access token",
             tags=["user"], response_model=Token)
async def refresh(
                  users: UserService = Depends(get_user_service),
                  current_user: UserModel = Depends(get_current_user_refresh),
                  access_service: AccessService = Depends(get_access_service),
                  refresh_service: RefreshService = Depends(get_refresh_service),
                  token: str = Depends(JWTBearer())
                  ):
    access_service.save_token(token=token)
    user = await users.get_by_id(user_id=current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED,
                            detail='Invalid refresh token')
    refresh_token = create_refresh_token(data={"user_id": user.id,
                                               "user_uuid": user.uuid})
    refresh_service.save_token(user_id=user.id, token=refresh_token)
    ref_id = decode_refresh_token(refresh_token).get("jti")
    access_token = create_access_token(data={"username": user.username,
                                             "email": user.email,
                                             "user_uuid": user.uuid,
                                             'refresh_uuid': ref_id,
                                             "user_id": user.id,
                                             "is_superuser": user.is_superuser,
                                             "created_at": str(user.created_at),
                                             'roles': user.roles})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )
