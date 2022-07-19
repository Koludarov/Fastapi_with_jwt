from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import JWTBearer, decode_access_token, create_access_token
from src.api.v1.schemas.users import UserCreate, UserModel, UserOut, UserIn, YourModel
from src.services.user import UserService, get_user_service, get_current_user

router = APIRouter()


@router.get(
    path="/me",
    response_model=UserOut,
    summary="Получить свои данные",
    tags=["user"],
)
async def get_user(token: str = Depends(JWTBearer()),
                   users: UserService = Depends(get_user_service)
                   ) -> UserModel:
    user_id: int = decode_access_token(token).get('user_id')
    return await users.get_by_id(user_id=user_id)


@router.post(
    path="/signup",
    response_model=UserOut,
    summary="Регистрация нового пользователя",
    tags=["user"],
    status_code=201
)
async def user_create(
        user: UserCreate, users: UserService = Depends(get_user_service),
):
    return await users.create_user(u=user)


@router.patch('/me', response_model=YourModel,
              summary="Обновить данные пользователя",
              tags=["user"])
async def update_user(
        user: UserIn,
        users: UserService = Depends(get_user_service),
        current_user: UserModel = Depends(get_current_user),
        token: str = Depends(JWTBearer()),
):
    old_user = await users.get_by_id(user_id=current_user.id)
    if old_user is None or old_user.email != current_user.email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    password = current_user.password
    uuid = current_user.uuid
    updated_user = await users.update(user_id=current_user.id,
                                      password=password,
                                      uuid=uuid,
                                      u=user
                                      )
    ref_id = decode_access_token(token).get("refresh_uuid")
    access_token = create_access_token(
        {"username": updated_user.username,
         "email": updated_user.email,
         "user_uuid": updated_user.uuid,
         'refresh_uuid': ref_id,
         "user_id": updated_user.id,
         "is_superuser": updated_user.is_superuser,
         "created_at": str(updated_user.created_at),
         'roles': updated_user.roles})
    return {'user': updated_user,
            'access_token': access_token}
