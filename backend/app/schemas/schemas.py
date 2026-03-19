from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    is_trial: bool
    trial_expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Guide Schemas
class StepBase(BaseModel):
    order: int
    title: str
    description: Optional[str] = None
    element_selector: str
    position: str = "bottom"
    config: Dict[str, Any] = {}


class StepCreate(StepBase):
    pass


class Step(StepBase):
    id: int
    guide_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GuideBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_url: str
    config: Dict[str, Any] = {}


class GuideCreate(GuideBase):
    steps: List[StepCreate] = []


class GuideUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None


class Guide(GuideBase):
    id: int
    is_published: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    steps: List[Step] = []

    class Config:
        from_attributes = True


# Page Analysis Schemas
class PageAnalysisRequest(BaseModel):
    url: str


class SuggestedElement(BaseModel):
    tag: str
    type: Optional[str] = ""
    id: Optional[str] = ""
    class_: Optional[str] = ""
    text: Optional[str] = ""
    title: str
    selector: str
    rect: Dict[str, int]
    center: Dict[str, int]


class PageAnalysisResponse(BaseModel):
    id: int
    url: str
    screenshot: Optional[str] = None  # base64 encoded image
    suggested_elements: List[SuggestedElement] = []
    analysis_result: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ElementFindRequest(BaseModel):
    url: str
    x: int
    y: int
    width: int
    height: int


class ElementFindResponse(BaseModel):
    tag: str
    id: Optional[str] = ""
    class_: Optional[str] = ""
    text: Optional[str] = ""
    selector: str
    rect: Dict[str, int]


# Code Generation Schema
class CodeGenerationRequest(BaseModel):
    guide_id: int
    format: str = "html"  # html, js, npm, json


class CodeGenerationResponse(BaseModel):
    code: str
    format: str
    instructions: str


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None