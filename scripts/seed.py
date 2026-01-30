from app.models.user import User
from app.models.category import Category
from app.core.security import get_password_hash
from app.core.database import get_session
from app.config import SEED_ADMIN_EMAIL, SEED_ADMIN_NAME, SEED_ADMIN_PASSWORD
import os
import asyncio
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

def parse_categories(raw: str) -> List[str]:
    return [c.strip() for c in raw.split(",") if c.strip()]

async def ensure_admin(session: AsyncSession) -> User:


    result = await session.execute(select(User).where(User.email == SEED_ADMIN_EMAIL))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        email=SEED_ADMIN_EMAIL,
        name=SEED_ADMIN_NAME,
        password_hash=get_password_hash(SEED_ADMIN_PASSWORD),
    )
    session.add(user)
    await session.flush()  # garante user.id
    return user


async def ensure_categories(session: AsyncSession, user: User) -> None:
    raw = os.getenv(
        "SEED_DEFAULT_CATEGORIES",
        "Alimentação,Transporte,Saúde,Lazer,Assinaturas,Contas,Compras,Investimentos",
    )
    names = parse_categories(raw)

    # pega categorias existentes do usuário
    result = await session.execute(
        select(Category.name).where(Category.user_id == user.id)
    )
    existing = {row[0] for row in result.all()}

    for name in names:
        if name in existing:
            continue
        session.add(Category(name=name, user_id=user.id))


async def main() -> None:
    async with get_session() as session:
        async with session.begin():
            user = await ensure_admin(session)
            await ensure_categories(session, user)

    print("✅ Seed concluído com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
