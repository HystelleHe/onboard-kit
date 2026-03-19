from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = users

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=True)
    trial_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    guides = relationship(Guide, back_populates=owner)
    usage_logs = relationship(UsageLog, back_populates=user)


class Guide(Base):
    __tablename__ = guides

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_url = Column(String, nullable=False)
    config = Column(JSON, nullable=False, default={})
    is_published = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey(users.id), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship(User, back_populates=guides)
    steps = relationship(Step, back_populates=guide, cascade=all, delete-orphan)
    screenshots = relationship(PageScreenshot, back_populates=guide, cascade=all, delete-orphan)


class Step(Base):
    __tablename__ = steps

    id = Column(Integer, primary_key=True, index=True)
    guide_id = Column(Integer, ForeignKey(guides.id), nullable=False)
    order = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    element_selector = Column(String, nullable=False)
    position = Column(String, default=bottom)
    config = Column(JSON, nullable=False, default={})
    # V2: 添加截图坐标支持
    screenshot_region = Column(JSON, nullable=True)  # {x, y, width, height}
    is_manual_selection = Column(Boolean, default=False)  # 是否是手动框选
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    guide = relationship(Guide, back_populates=steps)


class PageScreenshot(Base):
    V2: 存储页面截图
    __tablename__ = page_screenshots

    id = Column(Integer, primary_key=True, index=True)
    guide_id = Column(Integer, ForeignKey(guides.id), nullable=True)
    url = Column(String, nullable=False)
    screenshot_data = Column(LargeBinary, nullable=False)  # PNG 图片数据
    width = Column(Integer, nullable=False)  # 截图宽度
    height = Column(Integer, nullable=False)  # 截图高度
    suggested_regions = Column(JSON, nullable=True)  # AI推荐的交互区域
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    guide = relationship(Guide, back_populates=screenshots)


class PageAnalysis(Base):
    __tablename__ = page_analyses

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    html_content = Column(Text, nullable=True)
    analysis_result = Column(JSON, nullable=False, default={})
    suggested_elements = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UsageLog(Base):
    __tablename__ = usage_logs

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(users.id), nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship(User, back_populates=usage_logs)
