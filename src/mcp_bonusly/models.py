"""
Pydantic models for Bonusly API data structures.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr


class BonusUser(BaseModel):
    """Represents a user in the Bonusly system."""
    id: str
    short_name: str
    display_name: str
    username: str
    email: EmailStr
    path: str
    full_pic_url: Optional[str] = None
    profile_pic_url: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    last_active_at: Optional[datetime] = None
    external_unique_id: Optional[str] = None
    budget_boost: Optional[int] = 0
    user_mode: str = "normal"
    country: Optional[str] = None
    time_zone: Optional[str] = None
    can_give: bool = True
    earning_balance: int = 0
    earning_balance_with_currency: str = "0 points"
    lifetime_earnings: int = 0
    lifetime_earnings_with_currency: str = "0 points"
    can_receive: bool = True
    giving_balance: int = 0
    giving_balance_with_currency: str = "0 points"
    status: str = "active"


class Bonus(BaseModel):
    """Represents a bonus in the Bonusly system."""
    id: str
    created_at: datetime
    reason: str
    reason_html: Optional[str] = None
    amount: int
    amount_with_currency: str
    value: Optional[str] = None
    giver: BonusUser
    receiver: Optional[BonusUser] = None
    receivers: Optional[List[BonusUser]] = None
    child_count: int = 0
    child_bonuses: Optional[List["Bonus"]] = None
    via: Optional[str] = "api"
    family_amount: int = 0
    parent_bonus_id: Optional[str] = None
    hashtag: Optional[str] = None
    editable_until: Optional[datetime] = None


class BonusListResponse(BaseModel):
    """Response model for listing bonuses."""
    result: List[Bonus]
    meta: Optional[Dict[str, Any]] = None


class BonusResponse(BaseModel):
    """Response model for single bonus operations."""
    result: Bonus


class CreateBonusRequest(BaseModel):
    """Request model for creating a bonus."""
    giver_email: Optional[EmailStr] = Field(None, description="Email address of the person giving the bonus (admin only)")
    reason: str = Field(..., description="Reason for the bonus (e.g., '+10 @user for #teamwork')")
    parent_bonus_id: Optional[str] = Field(None, description="Parent bonus ID for replies")


class ListBonusesRequest(BaseModel):
    """Request model for listing bonuses."""
    limit: int = Field(20, ge=1, le=100, description="Number of bonuses to return")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    giver_email: Optional[EmailStr] = Field(None, description="Filter by giver's email")
    receiver_email: Optional[EmailStr] = Field(None, description="Filter by receiver's email")
    user_email: Optional[EmailStr] = Field(None, description="Filter by user's email (bonuses given or received)")
    hashtag: Optional[str] = Field(None, description="Filter by hashtag (e.g., #teamwork)")
    include_children: bool = Field(False, description="Include bonus replies")


class GetBonusRequest(BaseModel):
    """Request model for getting a specific bonus."""
    bonus_id: str = Field(..., description="ID of the bonus to retrieve")


# Update forward references
Bonus.model_rebuild() 