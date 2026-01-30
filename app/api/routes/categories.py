from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.category import Category
from app.dtos.category import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOut])
async def list_categories(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.user_id == user.id).order_by(Category.name.asc()))
    return [CategoryOut(id=c.id, name=c.name, color=c.color) for c in res.scalars().all()]

@router.post("", response_model=CategoryOut, status_code=201)
async def create_category(payload: CategoryCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # enforce unique (user_id, name) by constraint; handle friendly error
    c = Category(user_id=user.id, name=payload.name.strip(), color=payload.color)
    db.add(c)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Category name already exists")
    await db.refresh(c)
    return CategoryOut(id=c.id, name=c.name, color=c.color)

@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.id == category_id, Category.user_id == user.id))
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(c)
    await db.commit()
