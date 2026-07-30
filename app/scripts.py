import asyncio
from sqlalchemy import select
from models import User, Adv, Role, Right
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

    right_read_own_user = Right(
        read=True, write=False, only_own=True, model="User"
    )
    right_read_write_own_user = Right(
        read=True, write=True, only_own=True, model="User"
    )
    right_read_any_user = Right(
        read=True, write=False, only_own=False, model="User"
    )
    right_full_user = Right(
        read=True, write=True, only_own=False, model="User"
    )
    
    session.add_all([right_read_own_adv, right_read_write_own_adv, right_read_any_adv, right_full_adv, 
                     right_read_own_user, right_read_write_own_user, right_read_any_user, right_full_user])
    await session.flush()

    role_user = Role(name="user")
    role_user.rights = [right_read_own_adv, right_read_write_own_adv, right_read_any_adv, 
                        right_read_own_user, right_read_write_own_user, right_read_any_user]
    role_admin = Role(name="admin")
    role_admin.rights = [right_full_adv, right_full_user]
    session.add_all([role_user, role_admin])
    await session.flush()
    return role_user, role_admin

async def create_test_users(session, role_user, role_admin):
    hashed_pw_user = hash_password("1234")
    hashed_pw_admin = hash_password("admin5678")
    test_user = User(name="testuser", password=hashed_pw_user, roles=[role_user])
    test_admin = User(name="testadmin", password=hashed_pw_admin, roles=[role_admin])
    session.add_all[(test_user, test_admin)]
    await session.commit()
    print(f"Test user created with id: {test_user.id}")
    print(f"Test admin created with id: {test_admin.id}")

async def main():
    async with Session() as session:
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        if not existing_roles:
            print("Creating initial roles...")
            role_user, role_admin = await create_initial_roles(session)
            await create_test_users(session, role_user, role_admin)
            await session.commit()
            print("Initial data created.")
        else:
            print("Roles already exist.")
        
if __name__ == "__main__":
    asyncio.run(main())