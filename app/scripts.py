import asyncio
from sqlalchemy import select
from models import User, Role, Right
from database import Session
from auth import hash_password


async def create_initial_roles(session):
    right_read_own_adv = Right(
        read=True, write=False, only_own=True, model="Adv"
    )
    right_read_write_own_adv = Right(
        read=True, write=True, only_own=True, model="Adv"
    )
    right_read_any_adv = Right(
        read=True, write=False, only_own=False, model="Adv"
    )
    right_full_adv = Right(
        read=True, write=True, only_own=False, model="Adv"
    )
    session.add_all([right_read_own_adv, right_read_write_own_adv, right_read_any_adv, right_full_adv])
    await session.flush()

    role_user = Role(name="user")
    role_user.rights = [right_read_own_adv, right_read_write_own_adv]
    role_admin = Role(name="admin")
    role_admin.rights = [right_full_adv]
    session.add_all([role_user, role_admin])
    await session.flush()
    return role_user, role_admin

async def create_test_user(session, role_user):
    hashed_pw = hash_password("1234")
    test_user = User(name="testuser", password=hashed_pw, roles=[role_user])
    session.add(test_user)
    await session.commit()
    print(f"Test user created with id: {test_user.id}")

async def main():
    async with Session() as session:
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        if not existing_roles:
            print("Creating initial roles...")
            role_user, role_admin = await create_initial_roles(session)
            await create_test_user(session, role_user)
            await session.commit()
            print("Initial data created.")
        else:
            print("Roles already exist.")
        
if __name__ == "__main__":
    asyncio.run(main())