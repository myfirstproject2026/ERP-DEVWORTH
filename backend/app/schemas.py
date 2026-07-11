from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ============================================================
# AUTH
# ============================================================
class LoginRequest(BaseModel):
    identifier: str = Field(..., description="User ID or email")
    password: str
    keep_signed_in: bool = True


class OtpSendRequest(BaseModel):
    identifier: str


class OtpVerifyRequest(BaseModel):
    identifier: str
    otp_code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class MeOut(BaseModel):
    id: int
    full_name: str
    email: str
    role_name: str
    is_owner: bool
    company_id: int
    company_name: str
    branch_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# COMPANY REGISTRATION (multi-step wizard)
# ============================================================
class CompanyRegisterRequest(BaseModel):
    # Step 1 - Business info
    company_name: str
    business_type: str
    industry: str
    cin: Optional[str] = None
    contact_number: str
    business_email: EmailStr
    # Step 2 - Address & Tax
    address_line: str
    city: str
    state: str
    pin_code: str
    country: str = "India"
    gstin: str
    pan: str
    default_gst_rate: Decimal = Decimal("18.00")
    financial_year_start: str = "April"
    # Step 4 - owner login credentials
    owner_full_name: str
    owner_password: str


class CompanyOut(BaseModel):
    id: int
    company_name: str
    business_type: str
    industry: str
    cin: Optional[str]
    contact_number: str
    business_email: str
    address_line: str
    city: str
    state: str
    pin_code: str
    country: str
    gstin: str
    pan: str
    default_gst_rate: Decimal
    financial_year_start: str
    logo_url: Optional[str]
    plan_name: str
    plan_billing: str
    status: str
    member_since: date

    class Config:
        from_attributes = True


class CompanyUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    cin: Optional[str] = None
    contact_number: Optional[str] = None
    business_email: Optional[EmailStr] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    default_gst_rate: Optional[Decimal] = None
    financial_year_start: Optional[str] = None
    logo_url: Optional[str] = None


class CompanySnapshotOut(BaseModel):
    branches: int
    active_users: int
    roles_configured: int
    member_since: str


# ============================================================
# BRANCHES
# ============================================================
class BranchCreateRequest(BaseModel):
    branch_name: str
    branch_type: str = "Warehouse"
    address: str
    city: str
    state: str
    manager_user_id: Optional[int] = None
    gstin: Optional[str] = None
    is_default: bool = False


class BranchUpdateRequest(BaseModel):
    branch_name: Optional[str] = None
    branch_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    manager_user_id: Optional[int] = None
    gstin: Optional[str] = None
    status: Optional[str] = None
    is_default: Optional[bool] = None


class BranchOut(BaseModel):
    id: int
    branch_name: str
    branch_type: str
    address: str
    city: str
    state: str
    manager_name: Optional[str] = None
    manager_user_id: Optional[int] = None
    gstin: Optional[str]
    status: str
    users_count: int = 0
    is_default: bool

    class Config:
        from_attributes = True


class BranchStatsOut(BaseModel):
    total_branches: int
    active_branches: int
    inactive_branches: int
    total_staff: int


# ============================================================
# USERS
# ============================================================
class UserInviteRequest(BaseModel):
    full_name: str
    mobile_number: Optional[str] = None
    email: EmailStr
    role_id: int
    branch_id: int
    login_method: str = "email_invite"
    send_whatsapp_notification: bool = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    status: Optional[str] = None


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    mobile_number: Optional[str]
    role_id: int
    role_name: str
    branch_id: Optional[int]
    branch_name: Optional[str]
    status: str
    is_owner: bool

    class Config:
        from_attributes = True


class UserStatsOut(BaseModel):
    total_users: int
    active_users: int
    invited_users: int
    suspended_users: int


# ============================================================
# ROLES & PERMISSIONS
# ============================================================
class ModulePermissionItem(BaseModel):
    module_id: int
    module_key: str
    module_name: str
    can_view: bool
    can_add: bool
    can_edit: bool
    can_delete: bool
    can_approve: bool


class RoleCreateRequest(BaseModel):
    role_name: str
    description: Optional[str] = None
    access_level: str = "limited"


class RoleUpdateRequest(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    access_level: Optional[str] = None


class RolePermissionsUpdateRequest(BaseModel):
    permissions: List[ModulePermissionItem]


class RoleOut(BaseModel):
    id: int
    role_name: str
    description: Optional[str]
    access_level: str
    assigned_users: int = 0

    class Config:
        from_attributes = True


class RoleDetailOut(RoleOut):
    permissions: List[ModulePermissionItem]


# ============================================================
# DASHBOARD
# ============================================================
class DashboardSummaryOut(BaseModel):
    todays_sales: Decimal
    sales_change_pct: Decimal
    todays_purchase: Decimal
    purchase_change_pct: Decimal
    pending_payments: Decimal
    overdue_invoice_count: int
    stock_alert_count: int
    below_reorder_count: int
    ai_insight: str


class ProfitLossPointOut(BaseModel):
    month_label: str
    revenue_lakhs: Decimal
    net_profit_lakhs: Decimal


class ProductionOrderOut(BaseModel):
    wo_number: str
    product_name: str
    units: int
    stage: str
    progress_pct: int

    class Config:
        from_attributes = True


class AttendanceOut(BaseModel):
    present_count: int
    on_leave_count: int
    absent_count: int
    present_pct: int


class CustomerFollowUpOut(BaseModel):
    customer_name: str
    customer_type: Optional[str]
    city: Optional[str]
    amount: Decimal
    status: str
    days_overdue: int


# ============================================================
# AI ASSISTANT
# ============================================================
class AiMessageOut(BaseModel):
    id: int
    sender: str
    content: str
    payload_json: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AiAskRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class AiAskResponse(BaseModel):
    conversation_id: int
    user_message: AiMessageOut
    assistant_message: AiMessageOut


class ConnectedChannelOut(BaseModel):
    channel_name: str
    status: str

    class Config:
        from_attributes = True
