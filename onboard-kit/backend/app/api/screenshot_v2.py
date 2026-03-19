"""
V2 Screenshot API - Page analysis with screenshot support
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import base64

from app.core.database import get_db
from app.models.models import User as UserModel, Guide as GuideModel, PageScreenshot
from app.api.auth import get_current_user
from app.services.screenshot_analyzer import ScreenshotAnalyzerService, analyze_page_with_screenshot

router = APIRouter(prefix="/v2/screenshot", tags=["screenshot-v2"])


@router.post("/analyze")
async def analyze_with_screenshot(
    url: str,
    guide_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    V2: Analyze page with screenshot capture
    Returns screenshot as base64 and suggested interactive regions
    """
    try:
        # Capture and analyze page
        async with ScreenshotAnalyzerService() as service:
            result = await service.capture_and_analyze(url)
        
        # Convert screenshot to base64
        screenshot_base64 = base64.b64encode(result["screenshot"]).decode('utf-8')
        
        # Save to database if guide_id provided
        if guide_id:
            # Verify guide ownership
            guide_result = await db.execute(
                select(GuideModel).where(GuideModel.id == guide_id)
            )
            guide = guide_result.scalar_one_or_none()
            
            if guide and guide.owner_id == current_user.id:
                screenshot_record = PageScreenshot(
                    guide_id=guide_id,
                    url=url,
                    screenshot_data=result["screenshot"],
                    width=result["width"],
                    height=result["height"],
                    suggested_regions=result["suggested_regions"]
                )
                db.add(screenshot_record)
                await db.commit()
        
        return {
            "success": True,
            "data": {
                "screenshot": f"data:image/png;base64,{screenshot_base64}",
                "width": result["width"],
                "height": result["height"],
                "suggested_regions": result["suggested_regions"],
                "url": url
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot analysis failed: {str(e)}")


@router.get("/guide/{guide_id}")
async def get_guide_screenshots(
    guide_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all screenshots for a guide"""
    # Verify guide ownership
    result = await db.execute(
        select(GuideModel).where(GuideModel.id == guide_id)
    )
    guide = result.scalar_one_or_none()
    
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get screenshots
    screenshots_result = await db.execute(
        select(PageScreenshot)
        .where(PageScreenshot.guide_id == guide_id)
        .order_by(PageScreenshot.created_at.desc())
    )
    screenshots = screenshots_result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "url": s.url,
                "width": s.width,
                "height": s.height,
                "suggested_regions": s.suggested_regions,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in screenshots
        ]
    }


@router.get("/image/{screenshot_id}")
async def get_screenshot_image(
    screenshot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get screenshot image by ID"""
    result = await db.execute(
        select(PageScreenshot, GuideModel)
        .join(GuideModel, PageScreenshot.guide_id == GuideModel.id)
        .where(PageScreenshot.id == screenshot_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    screenshot, guide = row
    
    if guide.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    screenshot_base64 = base64.b64encode(screenshot.screenshot_data).decode('utf-8')
    
    return {
        "success": True,
        "data": {
            "screenshot": f"data:image/png;base64,{screenshot_base64}",
            "width": screenshot.width,
            "height": screenshot.height,
            "suggested_regions": screenshot.suggested_regions
        }
    }
