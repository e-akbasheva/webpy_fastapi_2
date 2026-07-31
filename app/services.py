from datetime import datetime, timezone

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Role, Right, Token, Adv, User
import schemas
from auth import check_password, hash_password, check_token, check_object_access


async def add_item(
        session: AsyncSession,
        token_obj: type[Token],
        orm_model: type[Adv],
        item_data: schemas.CreateAdvRequest
) -> Adv:
    """
    Создание записи и добавление в БД.
    """
    new_item = orm_model(
        title=item_data.title,
        description=item_data.description,
        price=item_data.price,
        user_id = token_obj.user_id
    )
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except IntegrityError as e:
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError) and e.orig.pgcode == '23505':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with such data already exists."
            )
        else:
            raise e


async def update_item(
        session: AsyncSession,
        orm_model: type[Adv],
        item_id: int,
        token_obj: type[Token],
        update_data: schemas.UpdateAdvRequest
) -> Adv:
    """
    Обновление объекта.
    """
    item = await get_item(session, orm_model, item_id)

    has_access = await check_item_access(
        session=session,
        orm_model=orm_model,
        item=item,
        item_id=item_id,
        token_obj=token_obj
    )

    if has_access:
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(item, key, value)

        await session.commit()
        await session.refresh(item)

        return item


async def delete_item(
        session: AsyncSession,
        orm_model: type[Adv],
        item_id: int,
        token_obj: type[Token],
) -> None:
    """
    Удаление объекта.
    """
    item = await get_item(session, orm_model, item_id)
    has_access = await check_item_access(
        session=session,
        orm_model=orm_model,
        item=item,
        item_id=item_id,
        token_obj=token_obj
    )
    
    if has_access:
        await session.delete(item)
        await session.commit()


async def get_item(
        session: AsyncSession,
        orm_model: type[Adv],
        item_id: int
) -> Adv:
    """
    Получение объекта по ID или выброс ошибки 404.
    """
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {item_id} not found"
        )
    
    return item


async def search_item(
        session: AsyncSession,
        orm_model: type[Adv],
        item_data: schemas.SearchAdvRequest
) -> Adv:
    """
    Поиск записи по полям.
    """
    item_dict = item_data.model_dump(exclude_unset=True)
    
    for key, value in item_dict.items():
        item_key = key
        match key:
            case 'title':
                stmt = select(orm_model).where(orm_model.title == value)
            case 'description':
                stmt = select(orm_model).where(orm_model.description == value)
            case 'price':
                stmt = select(orm_model).where(orm_model.price == value)
            case 'author':
                stmt = select(orm_model).where(orm_model.author == value)
            case 'created_at':
                stmt = select(orm_model).where(orm_model.created_at == value)    
    
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with key {item_key} not found"
        )
    return item


async def check_item_access(
        session: AsyncSession,
        orm_model: type[Adv],
        item: type[Adv],
        item_id: int,
        token_obj: type[Token]
): # -> Bool
    """
    Проверка доступа к записи или выброс ошибки 403.
    """
    has_access = await check_object_access(
        user=token_obj.user,
        orm_object=item,
        session=session,
        need_write=True
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access {orm_model.__name__} with id {item_id} denied"
        )
    else:
        return True

async def add_user(
        session: AsyncSession,
        orm_model: type[User],
        user_data: schemas.CreateUserRequest
) -> User:
    """
    Создание пользователя (с группой user).
    """
    hashed_password = hash_password(user_data.password)
    stmt = select(Role).where(Role.name == user_data.role)
    role = await session.scalar(stmt)

    new_user = orm_model(
        name=user_data.username, 
        password=hashed_password,
        roles=[role] if role else []
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
