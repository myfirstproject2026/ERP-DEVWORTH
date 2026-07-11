from sqlalchemy import (
    Column, BigInteger, String, Integer, DECIMAL, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, JSON, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class BusinessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Company(Base):
    __tablename__ = "companies"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_name = Column(String(150), nullable=False)
    business_type = Column(String(60), nullable=False)
    industry = Column(String(100), nullable=False)
    cin = Column(String(30))
    contact_number = Column(String(20), nullable=False)
    business_email = Column(String(150), nullable=False, unique=True)
    address_line = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pin_code = Column(String(10), nullable=False)
    country = Column(String(80), nullable=False, default="India")
    gstin = Column(String(20), nullable=False, unique=True)
    pan = Column(String(15), nullable=False)
    default_gst_rate = Column(DECIMAL(5, 2), nullable=False, default=18.00)
    financial_year_start = Column(String(20), nullable=False, default="April")
    logo_url = Column(String(255))
    plan_name = Column(String(60), nullable=False, default="Business")
    plan_billing = Column(String(30), nullable=False, default="billed annually")
    status = Column(Enum(BusinessStatus), nullable=False, default=BusinessStatus.active)
    member_since = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    branches = relationship("Branch", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan", foreign_keys="User.company_id")
    roles = relationship("Role", back_populates="company", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role_name = Column(String(80), nullable=False)
    description = Column(String(255))
    access_level = Column(Enum("full", "high", "medium", "limited", name="access_level_enum"), nullable=False, default="limited")
    is_system_role = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="roles")
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("company_id", "role_name", name="uq_role_per_company"),)


class Module(Base):
    __tablename__ = "modules"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    module_key = Column(String(60), nullable=False, unique=True)
    module_name = Column(String(100), nullable=False)
    category = Column(Enum("main", "login_setup", "workspace", name="module_category_enum"), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(BigInteger, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    can_view = Column(Boolean, default=False)
    can_add = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)

    role = relationship("Role", back_populates="permissions")
    module = relationship("Module")

    __table_args__ = (UniqueConstraint("role_id", "module_id", name="uq_role_module"),)


class Branch(Base):
    __tablename__ = "branches"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_name = Column(String(120), nullable=False)
    branch_type = Column(Enum("Head Office", "Warehouse", "Sales Office", "Plant", "Depot", "Other", name="branch_type_enum"), nullable=False, default="Warehouse")
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    manager_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    gstin = Column(String(20), nullable=True)
    status = Column(Enum("active", "inactive", name="branch_status_enum"), nullable=False, default="active")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="branches")
    manager = relationship("User", foreign_keys=[manager_user_id])
    users = relationship("User", back_populates="branch", foreign_keys="User.branch_id")


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(BigInteger, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False)
    mobile_number = Column(String(20))
    password_hash = Column(String(255), nullable=True)
    login_method = Column(Enum("password", "otp", "email_invite", name="login_method_enum"), nullable=False, default="email_invite")
    is_owner = Column(Boolean, default=False)
    status = Column(Enum("active", "invited", "suspended", name="user_status_enum"), nullable=False, default="invited")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="users", foreign_keys=[company_id])
    branch = relationship("Branch", back_populates="users", foreign_keys=[branch_id])
    role = relationship("Role", back_populates="users")

    __table_args__ = (UniqueConstraint("company_id", "email", name="uq_users_email_company"),)


class OtpRequest(Base):
    __tablename__ = "otp_requests"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Customer(Base):
    __tablename__ = "customers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(150), nullable=False)
    customer_type = Column(String(60))
    city = Column(String(100))
    zone = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    dues = relationship("CustomerDue", back_populates="customer", cascade="all, delete-orphan")


class CustomerDue(Base):
    __tablename__ = "customer_dues"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(14, 2), nullable=False)
    status = Column(Enum("overdue", "due_soon", "received", name="due_status_enum"), nullable=False)
    days_overdue = Column(Integer, default=0)
    last_order_days_ago = Column(Integer, nullable=True)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="dues")


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    metric_date = Column(Date, nullable=False)
    todays_sales = Column(DECIMAL(14, 2), default=0)
    sales_change_pct = Column(DECIMAL(6, 2), default=0)
    todays_purchase = Column(DECIMAL(14, 2), default=0)
    purchase_change_pct = Column(DECIMAL(6, 2), default=0)
    pending_payments = Column(DECIMAL(14, 2), default=0)
    overdue_invoice_count = Column(Integer, default=0)
    stock_alert_count = Column(Integer, default=0)
    below_reorder_count = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("company_id", "metric_date", name="uq_dm_company_date"),)


class ProfitLossMonthly(Base):
    __tablename__ = "profit_loss_monthly"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    month_label = Column(String(10), nullable=False)
    month_order = Column(Integer, nullable=False)
    revenue_lakhs = Column(DECIMAL(10, 2), nullable=False)
    net_profit_lakhs = Column(DECIMAL(10, 2), nullable=False)


class ProductionOrder(Base):
    __tablename__ = "production_orders"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    wo_number = Column(String(30), nullable=False)
    product_name = Column(String(150), nullable=False)
    units = Column(Integer, nullable=False)
    stage = Column(String(80), nullable=False)
    progress_pct = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class AttendanceDaily(Base):
    __tablename__ = "attendance_daily"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    present_count = Column(Integer, default=0)
    on_leave_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("company_id", "attendance_date", name="uq_att_company_date"),)


class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(150), nullable=False)
    units_sold_month = Column(Integer, default=0)
    change_pct = Column(DECIMAL(6, 2), default=0)
    current_stock = Column(Integer, default=0)
    daily_run_rate = Column(DECIMAL(8, 2), default=0)
    supplier_price = Column(DECIMAL(10, 2), default=0)
    reorder_suggested_units = Column(Integer, default=0)


class AiConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False, default="New conversation")
    created_at = Column(DateTime, server_default=func.now())

    messages = relationship("AiMessage", back_populates="conversation", cascade="all, delete-orphan")


class AiMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(Enum("user", "assistant", name="ai_sender_enum"), nullable=False)
    content = Column(Text, nullable=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("AiConversation", back_populates="messages")


class ConnectedChannel(Base):
    __tablename__ = "connected_channels"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    channel_name = Column(String(60), nullable=False)
    status = Column(Enum("connected", "disconnected", name="channel_status_enum"), nullable=False, default="disconnected")

    __table_args__ = (UniqueConstraint("company_id", "channel_name", name="uq_cc_company_channel"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(120), nullable=False)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
