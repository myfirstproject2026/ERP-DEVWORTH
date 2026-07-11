-- ============================================================
-- NEXUS ERP - MySQL Database Schema
-- Module: Login & Company Setup + Dashboard + AI Assistant
-- ============================================================

CREATE DATABASE IF NOT EXISTS nexus_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nexus_erp;

-- ============================================================
-- COMPANIES
-- ============================================================
CREATE TABLE companies (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_name        VARCHAR(150) NOT NULL,
    business_type       VARCHAR(60)  NOT NULL,
    industry            VARCHAR(100) NOT NULL,
    cin                 VARCHAR(30),
    contact_number      VARCHAR(20)  NOT NULL,
    business_email      VARCHAR(150) NOT NULL,
    address_line        VARCHAR(255) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    pin_code            VARCHAR(10)  NOT NULL,
    country             VARCHAR(80)  NOT NULL DEFAULT 'India',
    gstin               VARCHAR(20)  NOT NULL,
    pan                 VARCHAR(15)  NOT NULL,
    default_gst_rate    DECIMAL(5,2) NOT NULL DEFAULT 18.00,
    financial_year_start VARCHAR(20) NOT NULL DEFAULT 'April',
    logo_url            VARCHAR(255),
    plan_name           VARCHAR(60)  NOT NULL DEFAULT 'Business',
    plan_billing        VARCHAR(30)  NOT NULL DEFAULT 'billed annually',
    status              ENUM('active','inactive') NOT NULL DEFAULT 'active',
    member_since        DATE NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_companies_gstin (gstin),
    UNIQUE KEY uq_companies_email (business_email),
    INDEX idx_companies_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- ROLES  (per-company custom roles)
-- ============================================================
CREATE TABLE roles (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    role_name       VARCHAR(80) NOT NULL,
    description     VARCHAR(255),
    access_level    ENUM('full','high','medium','limited') NOT NULL DEFAULT 'limited',
    is_system_role  TINYINT(1) NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_roles_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY uq_role_per_company (company_id, role_name),
    INDEX idx_roles_company (company_id)
) ENGINE=InnoDB;

-- ============================================================
-- MODULES (static reference list — matches sidebar)
-- ============================================================
CREATE TABLE modules (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    module_key    VARCHAR(60) NOT NULL UNIQUE,
    module_name   VARCHAR(100) NOT NULL,
    category      ENUM('main','login_setup','workspace') NOT NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    is_active     TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

-- ============================================================
-- ROLE_PERMISSIONS  (module-level grid: view/add/edit/delete/approve)
-- ============================================================
CREATE TABLE role_permissions (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role_id       BIGINT UNSIGNED NOT NULL,
    module_id     BIGINT UNSIGNED NOT NULL,
    can_view      TINYINT(1) NOT NULL DEFAULT 0,
    can_add       TINYINT(1) NOT NULL DEFAULT 0,
    can_edit      TINYINT(1) NOT NULL DEFAULT 0,
    can_delete    TINYINT(1) NOT NULL DEFAULT 0,
    can_approve   TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rp_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    UNIQUE KEY uq_role_module (role_id, module_id),
    INDEX idx_rp_role (role_id)
) ENGINE=InnoDB;

-- ============================================================
-- BRANCHES
-- ============================================================
CREATE TABLE branches (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    branch_name     VARCHAR(120) NOT NULL,
    branch_type     ENUM('Head Office','Warehouse','Sales Office','Plant','Depot','Other') NOT NULL DEFAULT 'Warehouse',
    address         VARCHAR(255) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(100) NOT NULL,
    manager_user_id BIGINT UNSIGNED NULL,
    gstin           VARCHAR(20) NULL,
    status          ENUM('active','inactive') NOT NULL DEFAULT 'active',
    is_default      TINYINT(1) NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_branches_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_branches_company (company_id),
    INDEX idx_branches_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    branch_id       BIGINT UNSIGNED NULL,
    role_id         BIGINT UNSIGNED NOT NULL,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(150) NOT NULL,
    mobile_number   VARCHAR(20),
    password_hash   VARCHAR(255) NULL,
    login_method    ENUM('password','otp','email_invite') NOT NULL DEFAULT 'email_invite',
    is_owner        TINYINT(1) NOT NULL DEFAULT 0,
    status          ENUM('active','invited','suspended') NOT NULL DEFAULT 'invited',
    last_login_at   TIMESTAMP NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_users_branch  FOREIGN KEY (branch_id)  REFERENCES branches(id) ON DELETE SET NULL,
    CONSTRAINT fk_users_role    FOREIGN KEY (role_id)    REFERENCES roles(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_users_email_company (company_id, email),
    INDEX idx_users_company (company_id),
    INDEX idx_users_status (status),
    INDEX idx_users_branch (branch_id)
) ENGINE=InnoDB;

ALTER TABLE branches
    ADD CONSTRAINT fk_branch_manager FOREIGN KEY (manager_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- ============================================================
-- OTP LOGIN
-- ============================================================
CREATE TABLE otp_requests (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT UNSIGNED NOT NULL,
    otp_code      VARCHAR(6) NOT NULL,
    is_used       TINYINT(1) NOT NULL DEFAULT 0,
    expires_at    TIMESTAMP NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_otp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_otp_user (user_id)
) ENGINE=InnoDB;

-- ============================================================
-- CUSTOMERS  (for dashboard follow-up + AI assistant)
-- ============================================================
CREATE TABLE customers (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    customer_name   VARCHAR(150) NOT NULL,
    customer_type   VARCHAR(60),
    city            VARCHAR(100),
    zone            VARCHAR(100),
    phone           VARCHAR(20),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customers_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_customers_company (company_id)
) ENGINE=InnoDB;

CREATE TABLE customer_dues (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id     BIGINT UNSIGNED NOT NULL,
    company_id      BIGINT UNSIGNED NOT NULL,
    amount          DECIMAL(14,2) NOT NULL,
    status          ENUM('overdue','due_soon','received') NOT NULL,
    days_overdue    INT NOT NULL DEFAULT 0,
    last_order_days_ago INT NULL,
    due_date        DATE NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cd_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    CONSTRAINT fk_cd_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_cd_company (company_id),
    INDEX idx_cd_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- DASHBOARD METRICS
-- ============================================================
CREATE TABLE daily_metrics (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id      BIGINT UNSIGNED NOT NULL,
    metric_date     DATE NOT NULL,
    todays_sales    DECIMAL(14,2) NOT NULL DEFAULT 0,
    sales_change_pct DECIMAL(6,2) NOT NULL DEFAULT 0,
    todays_purchase DECIMAL(14,2) NOT NULL DEFAULT 0,
    purchase_change_pct DECIMAL(6,2) NOT NULL DEFAULT 0,
    pending_payments DECIMAL(14,2) NOT NULL DEFAULT 0,
    overdue_invoice_count INT NOT NULL DEFAULT 0,
    stock_alert_count INT NOT NULL DEFAULT 0,
    below_reorder_count INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_dm_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY uq_dm_company_date (company_id, metric_date)
) ENGINE=InnoDB;

CREATE TABLE profit_loss_monthly (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    month_label   VARCHAR(10) NOT NULL,
    month_order   INT NOT NULL,
    revenue_lakhs DECIMAL(10,2) NOT NULL,
    net_profit_lakhs DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_pl_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_pl_company (company_id)
) ENGINE=InnoDB;

CREATE TABLE production_orders (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    wo_number     VARCHAR(30) NOT NULL,
    product_name  VARCHAR(150) NOT NULL,
    units         INT NOT NULL,
    stage         VARCHAR(80) NOT NULL,
    progress_pct  INT NOT NULL DEFAULT 0,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_po_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_po_company (company_id)
) ENGINE=InnoDB;

CREATE TABLE attendance_daily (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    attendance_date DATE NOT NULL,
    present_count INT NOT NULL DEFAULT 0,
    on_leave_count INT NOT NULL DEFAULT 0,
    absent_count  INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_att_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY uq_att_company_date (company_id, attendance_date)
) ENGINE=InnoDB;

-- ============================================================
-- PRODUCTS  (for AI assistant "fast moving product" queries)
-- ============================================================
CREATE TABLE products (
    id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id        BIGINT UNSIGNED NOT NULL,
    product_name      VARCHAR(150) NOT NULL,
    units_sold_month  INT NOT NULL DEFAULT 0,
    change_pct        DECIMAL(6,2) NOT NULL DEFAULT 0,
    current_stock     INT NOT NULL DEFAULT 0,
    daily_run_rate    DECIMAL(8,2) NOT NULL DEFAULT 0,
    supplier_price    DECIMAL(10,2) NOT NULL DEFAULT 0,
    reorder_suggested_units INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_products_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_products_company (company_id)
) ENGINE=InnoDB;

-- ============================================================
-- AI ASSISTANT
-- ============================================================
CREATE TABLE ai_conversations (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    user_id       BIGINT UNSIGNED NOT NULL,
    title         VARCHAR(150) NOT NULL DEFAULT 'New conversation',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aic_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_aic_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_aic_company (company_id)
) ENGINE=InnoDB;

CREATE TABLE ai_messages (
    id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    conversation_id   BIGINT UNSIGNED NOT NULL,
    sender            ENUM('user','assistant') NOT NULL,
    content           TEXT NOT NULL,
    payload_json      JSON NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aim_conv FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE,
    INDEX idx_aim_conv (conversation_id)
) ENGINE=InnoDB;

CREATE TABLE connected_channels (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    channel_name  VARCHAR(60) NOT NULL,
    status        ENUM('connected','disconnected') NOT NULL DEFAULT 'disconnected',
    CONSTRAINT fk_cc_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY uq_cc_company_channel (company_id, channel_name)
) ENGINE=InnoDB;

-- ============================================================
-- AUDIT LOG
-- ============================================================
CREATE TABLE audit_logs (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    company_id    BIGINT UNSIGNED NOT NULL,
    user_id       BIGINT UNSIGNED NULL,
    action        VARCHAR(120) NOT NULL,
    entity_type   VARCHAR(60) NOT NULL,
    entity_id     BIGINT UNSIGNED NULL,
    details       JSON NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_audit_company (company_id)
) ENGINE=InnoDB;
