from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.models import User as UserModel, Guide as GuideModel, Step as StepModel, UsageLog
from app.schemas.schemas import Guide, GuideCreate, GuideUpdate
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=Guide, status_code=status.HTTP_201_CREATED)
async def create_guide(
    guide_in: GuideCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 创建引导配置
    db_guide = GuideModel(
        name=guide_in.name,
        description=guide_in.description,
        target_url=guide_in.target_url,
        config=guide_in.config,
        owner_id=current_user.id
    )
    db.add(db_guide)
    await db.flush()

    # 创建步骤
    for step_data in guide_in.steps:
        db_step = StepModel(
            guide_id=db_guide.id,
            **step_data.model_dump()
        )
        db.add(db_step)

    # 记录使用日志
    log = UsageLog(
        user_id=current_user.id,
        action="create_guide",
        details={"guide_name": guide_in.name}
    )
    db.add(log)

    await db.commit()
    await db.refresh(db_guide)

    # 重新查询以包含steps
    result = await db.execute(
        select(GuideModel)
        .options(selectinload(GuideModel.steps))
        .where(GuideModel.id == db_guide.id)
    )
    guide = result.scalar_one()
    return guide


@router.get("/", response_model=List[Guide])
async def list_guides(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    result = await db.execute(
        select(GuideModel)
        .options(selectinload(GuideModel.steps))
        .where(GuideModel.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    guides = result.scalars().all()
    return guides


@router.get("/{guide_id}", response_model=Guide)
async def get_guide(
    guide_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    result = await db.execute(
        select(GuideModel)
        .options(selectinload(GuideModel.steps))
        .where(GuideModel.id == guide_id)
    )
    guide = result.scalar_one_or_none()

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return guide


@router.put("/{guide_id}", response_model=Guide)
async def update_guide(
    guide_id: int,
    guide_in: GuideUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    result = await db.execute(
        select(GuideModel).where(GuideModel.id == guide_id)
    )
    guide = result.scalar_one_or_none()

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 更新字段
    update_data = guide_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guide, field, value)

    await db.commit()
    await db.refresh(guide)

    # 重新查询以包含steps
    result = await db.execute(
        select(GuideModel)
        .options(selectinload(GuideModel.steps))
        .where(GuideModel.id == guide_id)
    )
    guide = result.scalar_one()
    return guide


@router.delete("/{guide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guide(
    guide_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    result = await db.execute(
        select(GuideModel).where(GuideModel.id == guide_id)
    )
    guide = result.scalar_one_or_none()

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(guide)
    await db.commit()
    return None
