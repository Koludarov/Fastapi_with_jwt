from fastapi import APIRouter, Depends, HTTPException, status

from src.api.v1.schemas.users import UserModel
from src.services.user import get_current_user
from src.services.user import UserService, get_user_service
from src.core.security import JWTBearer
from src.services.reshresh_token import RefreshService, get_refresh_service
from src.services.access_token import AccessService, get_access_service

router = APIRouter()


@router.post("/",
             summary="Выход со всех устройств",
             tags=["user"])
async def logout(users: UserService = Depends(get_user_service),
                 current_user: UserModel = Depends(get_current_user),
                 refresh_service: RefreshService = Depends(get_refresh_service),
                 access_service: AccessService = Depends(get_access_service),
                 token: str = Depends(JWTBearer())):
    user = await users.get_by_id(user_id=current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED,
                            detail='Not authorized')
    access_service.save_token(token=token)
    refresh_service.remove_all_refresh_token(user_id=user.id)
    return {"msg": "You have been log out from all devices"}
