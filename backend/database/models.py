from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    password_hash: str
    name: str
    analyses_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    linked_in: Optional[str] = None
    profile_photo: Optional[str] = None
    is_verified: bool
    analyses_count: int
    created_at: datetime
    deletion_at: Optional[datetime] = None

class CancelDeletionRequest(BaseModel):
    email: EmailStr

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    linked_in: Optional[str] = None
    profile_photo: Optional[str] = None

class DeleteAccountRequest(BaseModel):
    email: EmailStr

class DeleteAccountConfirm(BaseModel):
    email: EmailStr
    otp: str
    identity_key: str

class IdentityKeyRequest(BaseModel):
    email: EmailStr

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class AnalysisMeta(BaseModel):
    fact_checks_found: int = 0
    news_found: int = 0

class Source(BaseModel):
    title: str
    url: str
    publisher: Optional[str] = None
    type: str # "news" or "fact_check" or "wikipedia"

class Analysis(BaseModel):
    request_id: str
    claim: str
    clean_claim: str
    score: int
    verdict: str
    confidence: int
    summary: str
    hindi_summary: str
    flags: List[dict] = []
    indicators: List[dict] = []
    sources: List[dict] = []
    tips: List[dict] = []
    meta: AnalysisMeta = AnalysisMeta()
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
