from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db_session
from lifespan import lifespan
from services import add_item, get_item, update_item, delete_item, search_item, add_user

from models import Adv, User, Token
from sqlalchemy import select

from auth import check_password, hash_password, check_token, check_object_access


app = FastAPI(
    title="My Adv App",
    description="This is an advertisement application API",
    version="0.0.2",
    lifespan=lifespan
)


@app.post("/advertisement", response_model=schemas.CreateAdvResponse, summary="Создать новое объявление") # юзер
async def create_adv(
        adv_data: schemas.CreateAdvRequest,
        token_obj: Token = Depends(check_token),
        session: AsyncSession = Depends(get_db_session)
):
    new_adv = await add_item(session, token_obj, Adv, adv_data)
    return schemas.CreateAdvResponse(id=new_adv.id)


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.UpdateAdvResponse, summary="Обновить объявление") # юзер (свое)
async def update_adv(
        advertisement_id: int,
        update_data: schemas.UpdateAdvRequest,
        token_obj: Token = Depends(check_token),
        session: AsyncSession = Depends(get_db_session)
):
    updated_adv = await update_item(session, Adv, advertisement_id, token_obj, update_data)
    return schemas.UpdateAdvResponse(**updated_adv.to_dict())


@app.delete("/advertisement/{advertisement_id}", response_model=schemas.OKResponse, summary="Удалить объявление") # юзер (свое)
async def delete_adv(
        advertisement_id: int,
        token_obj: Token = Depends(check_token),
        session: AsyncSession = Depends(get_db_session)
):
    await delete_item(session, Adv, advertisement_id, token_obj)
    return schemas.OKResponse()


@app.get("/advertisement/{advertisement_id}", response_model=schemas.GetAdvResponse, summary="Получить объявление по ID") # без токена
async def get_adv(
        advertisement_id: int,
        session: AsyncSession = Depends(get_db_session),
):
    adv = await get_item(session, Adv, advertisement_id)
    return schemas.GetAdvResponse(**adv.to_dict())


@app.get("/advertisement", response_model=schemas.SearchAdvResponse, summary="Найти объявление по полю") # без токена
async def search_adv(
        advertisement_data: schemas.SearchAdvRequest,
        session: AsyncSession = Depends(get_db_session)
):
    searched_adv = await search_item(session, Adv, advertisement_data)
    return schemas.SearchAdvResponse(**searched_adv.to_dict())


@app.post("/login", response_model=schemas.LoginResponse, summary="Залогиниться")
async def login(
        login_data: schemas.LoginRequest,
        session: AsyncSession = Depends(get_db_session)
):
    query = select(User).where(User.name == login_data.username)
    user = await session.scalar(query)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    
    if not check_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    
    new_token = Token(user=user)
    session.add(new_token)
    await session.commit()
    await session.refresh(new_token)

    return new_token


@app.post("/user", response_model=schemas.IdResponse, summary="Создать пользователя") # без токена
async def create_user(
        user_data: schemas.CreateUserRequest,
        session: AsyncSession = Depends(get_db_session)
):
    new_user = await add_user(session, User, user_data)
    return schemas.IdResponse(id=new_user.id)

@app.get("/user/{user_id}", response_model=schemas.GetUserResponse, summary="Получить пользователя по id") # без токена
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    user = await get_item(session, User, user_id)
    return schemas.GetUserResponse(**user.to_dict())

@app.patch("/user/{user_id}", response_model=schemas.UpdateUserResponse, summary="Обновить пользователя") # юзер (своих данных)
async def update_user(
        user_id: int,
        update_data: schemas.UpdateUserRequest,
        session: AsyncSession = Depends(get_db_session),
        token_obj: Token = Depends(check_token)
):
    updated_user = await update_item(session, User, user_id, token_obj, update_data)
    return schemas.UpdateUserResponse(**updated_user.to_dict())

@app.delete("/user/{user_id}", response_model=schemas.OKResponse, summary="Удалить пользователя") # юзер (себя)
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_db_session),
        token_obj: Token = Depends(check_token)
):
    await delete_item(session, User, user_id, token_obj)
    return schemas.OKResponse()