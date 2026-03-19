from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import User as UserModel, Guide as GuideModel, PageAnalysis as PageAnalysisModel, UsageLog
from app.schemas.schemas import (
    PageAnalysisRequest,
    PageAnalysisResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
    ElementFindRequest,
    ElementFindResponse
)
from app.api.auth import get_current_user
from app.services.page_analyzer import PageAnalyzerService
from app.services.code_generator import CodeGeneratorService

router = APIRouter()


@router.post("/analyze", response_model=PageAnalysisResponse)
async def analyze_page(
    request: PageAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    分析目标页面，截图并提取可交互元素
    """
    try:
        # 使用Playwright分析页面
        analyzer = PageAnalyzerService()
        analysis_result = await analyzer.analyze_url(request.url)

        # 保存分析结果
        db_analysis = PageAnalysisModel(
            url=request.url,
            html_content=analysis_result.get("html_content"),
            analysis_result=analysis_result.get("structure", {}),
            suggested_elements=analysis_result.get("suggested_elements", [])
        )
        db.add(db_analysis)

        # 记录使用日志
        log = UsageLog(
            user_id=current_user.id,
            action="analyze_page",
            details={"url": request.url}
        )
        db.add(log)

        await db.commit()
        await db.refresh(db_analysis)

        # 返回结果（包含截图和推荐元素）
        return {
            "id": db_analysis.id,
            "url": db_analysis.url,
            "screenshot": analysis_result.get("screenshot"),
            "suggested_elements": analysis_result.get("suggested_elements", []),
            "analysis_result": analysis_result.get("structure", {}),
            "created_at": db_analysis.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze page: {str(e)}")


@router.post("/find-element", response_model=ElementFindResponse)
async def find_element_by_coordinate(
    request: ElementFindRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    根据坐标查找页面元素
    """
    try:
        analyzer = PageAnalyzerService()
        element_info = await analyzer.find_element_by_coordinate(
            request.url, 
            request.x, 
            request.y, 
            request.width, 
            request.height
        )
        
        if not element_info:
            raise HTTPException(status_code=404, detail="No element found at the specified coordinates")
        
        return element_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find element: {str(e)}")


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    根据引导配置生成可集成的代码
    """
    # 获取引导配置
    result = await db.execute(
        select(GuideModel)
        .options(selectinload(GuideModel.steps))
        .where(GuideModel.id == request.guide_id)
    )
    guide = result.scalar_one_or_none()

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 生成代码
    generator = CodeGeneratorService()
    code_result = generator.generate(guide, request.format)

    # 记录使用日志
    log = UsageLog(
        user_id=current_user.id,
        action="generate_code",
        details={"guide_id": request.guide_id, "format": request.format}
    )
    db.add(log)
    await db.commit()

    return CodeGenerationResponse(
        code=code_result["code"],
        format=request.format,
        instructions=code_result["instructions"]
    )


@router.get("/preview/{guide_id}")
async def preview_guide(
    guide_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取引导预览数据
    """
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

    # 记录使用日志
    log = UsageLog(
        user_id=current_user.id,
        action="preview",
        details={"guide_id": guide_id}
    )
    db.add(log)
    await db.commit()

    # 转换为Driver.js配置格式
    steps_config = []
    for step in sorted(guide.steps, key=lambda s: s.order):
        steps_config.append({
            "element": step.element_selector,
            "popover": {
                "title": step.title,
                "description": step.description or "",
                "side": step.position or "bottom",
                "align": "start"
            }
        })

    return {
        "guide": {
            "id": guide.id,
            "name": guide.name,
            "target_url": guide.target_url
        },
        "steps": steps_config,
        "config": guide.config
    }