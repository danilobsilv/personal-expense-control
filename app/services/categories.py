from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.category import Category

async def ensure_category_belongs_to_user(db: AsyncSession, user_id: int, category_id: int) -> None:
    res = await db.execute(select(Category.id).where(Category.id == category_id, Category.user_id == user_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail="Invalid category_id")
