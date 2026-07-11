-- ============================================================
-- SEED DATA — matches the PDF screens exactly
-- ============================================================
USE nexus_erp;

-- MODULES (sidebar) ------------------------------------------------
INSERT INTO modules (module_key, module_name, category, sort_order, is_active) VALUES
('dashboard', 'Dashboard', 'main', 1, 1),
('company_profile', 'Company Profile', 'login_setup', 2, 1),
('branches', 'Branches', 'login_setup', 3, 1),
('users', 'Users', 'login_setup', 4, 1),
('roles_permissions', 'Roles & Permissions', 'login_setup', 5, 1),
('sales_crm', 'Sales + CRM', 'workspace', 6, 0),
('inventory', 'Inventory', 'workspace', 7, 0),
('purchase', 'Purchase', 'workspace', 8, 0),
('manufacturing', 'Manufacturing', 'workspace', 9, 0),
('hr_employee', 'HR & Employee', 'workspace', 10, 0),
('finance_gst', 'Finance & GST', 'workspace', 11, 0),
('service_desk', 'Service Desk', 'workspace', 12, 0),
('company_settings', 'Company Settings', 'login_setup', 13, 1);

-- COMPANY -----------------------------------------------------------
INSERT INTO companies
(company_name, business_type, industry, cin, contact_number, business_email,
 address_line, city, state, pin_code, country, gstin, pan, default_gst_rate,
 financial_year_start, plan_name, plan_billing, status, member_since)
VALUES
('Sundar Precision Pvt Ltd', 'Private Limited Company', 'Manufacturing — Precision Tooling',
 'U29100TN2015PTC098234', '+91 98410 22456', 'accounts@sundarprecision.com',
 'Plot 14, SIDCO Industrial Estate, Ambattur', 'Chennai', 'Tamil Nadu', '600058', 'India',
 '33AAECS1234F1Z5', 'AAECS1234F', 18.00, 'April', 'Business', 'billed annually', 'active', '2022-03-01');

SET @company_id = LAST_INSERT_ID();

-- ROLES ---------------------------------------------------------------
INSERT INTO roles (company_id, role_name, description, access_level, is_system_role) VALUES
(@company_id, 'Owner', 'Full access to all modules and settings', 'full', 1),
(@company_id, 'Manager', 'Access to all modules, no billing/settings', 'high', 0),
(@company_id, 'Branch Manager', 'Manage assigned branch operations', 'medium', 0),
(@company_id, 'Sales Staff', 'Sales, CRM and quotations only', 'limited', 0),
(@company_id, 'Accountant', 'Finance, GST and payment modules', 'limited', 0),
(@company_id, 'Production Staff', 'Manufacturing and inventory only', 'limited', 0);

SET @role_owner = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Owner');
SET @role_manager = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Manager');
SET @role_branch_mgr = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Branch Manager');
SET @role_sales = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Sales Staff');
SET @role_accountant = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Accountant');
SET @role_production = (SELECT id FROM roles WHERE company_id=@company_id AND role_name='Production Staff');

-- BRANCHES (created before users, manager linked after) ---------------
INSERT INTO branches (company_id, branch_name, branch_type, address, city, state, status, is_default) VALUES
(@company_id, 'Chennai HQ (Head Office)', 'Head Office', 'Plot 14, SIDCO Industrial Estate, Ambattur', 'Chennai', 'Tamil Nadu', 'active', 1),
(@company_id, 'Coimbatore Plant', 'Plant', '44/2, SIPCOT Industrial Park, Coimbatore', 'Coimbatore', 'Tamil Nadu', 'active', 0),
(@company_id, 'Bengaluru Sales Office', 'Sales Office', 'No.9, Residency Road, Bengaluru', 'Bengaluru', 'Karnataka', 'active', 0),
(@company_id, 'Hyderabad Depot', 'Depot', 'Plot 7, Kukatpally Industrial Area', 'Hyderabad', 'Telangana', 'inactive', 0);

SET @branch_chennai = (SELECT id FROM branches WHERE company_id=@company_id AND branch_name='Chennai HQ (Head Office)');
SET @branch_coimbatore = (SELECT id FROM branches WHERE company_id=@company_id AND branch_name='Coimbatore Plant');
SET @branch_bengaluru = (SELECT id FROM branches WHERE company_id=@company_id AND branch_name='Bengaluru Sales Office');
SET @branch_hyderabad = (SELECT id FROM branches WHERE company_id=@company_id AND branch_name='Hyderabad Depot');

-- USERS -----------------------------------------------------------------
-- password for all seed users = "Password@123" (bcrypt hash placeholder, replaced by app on first run/seed script)
INSERT INTO users (company_id, branch_id, role_id, full_name, email, mobile_number, password_hash, login_method, is_owner, status) VALUES
(@company_id, @branch_chennai, @role_owner, 'Ravi Kumar', 'ravi@sundarprecision.com', '+91 98410 22456', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 1, 'active'),
(@company_id, @branch_coimbatore, @role_manager, 'Meena Iyer', 'meena@sundarprecision.com', '+91 90000 11111', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_bengaluru, @role_sales, 'Arjun Das', 'arjun@sundarprecision.com', '+91 90000 22222', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_hyderabad, @role_branch_mgr, 'Priya Reddy', 'priya@sundarprecision.com', '+91 90000 33333', NULL, 'email_invite', 0, 'invited'),
(@company_id, @branch_chennai, @role_accountant, 'Karthik S', 'karthik@sundarprecision.com', '+91 90000 44444', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_coimbatore, @role_production, 'Divya Menon', 'divya@sundarprecision.com', '+91 90000 55555', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'suspended');

-- remaining 12 users to reach "18 users across 4 branches" -----------
INSERT INTO users (company_id, branch_id, role_id, full_name, email, mobile_number, password_hash, login_method, is_owner, status) VALUES
(@company_id, @branch_chennai, @role_sales, 'Deepak Nair', 'deepak@sundarprecision.com', '+91 90000 66666', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_chennai, @role_sales, 'Sneha Rao', 'sneha@sundarprecision.com', '+91 90000 77777', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_bengaluru, @role_sales, 'Farhan Sheikh', 'farhan@sundarprecision.com', '+91 90000 88888', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_coimbatore, @role_sales, 'Anita George', 'anita@sundarprecision.com', '+91 90000 99999', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_bengaluru, @role_sales, 'Vikram Shah', 'vikram@sundarprecision.com', '+91 90001 11111', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_chennai, @role_accountant, 'Lakshmi Prasad', 'lakshmi@sundarprecision.com', '+91 90001 22222', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_coimbatore, @role_production, 'Suresh Babu', 'suresh@sundarprecision.com', '+91 90001 33333', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_coimbatore, @role_branch_mgr, 'Ramesh Pillai', 'ramesh@sundarprecision.com', '+91 90001 44444', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_bengaluru, @role_branch_mgr, 'Kavya Menon', 'kavya@sundarprecision.com', '+91 90001 55555', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_hyderabad, @role_branch_mgr, 'Naveen Kumar', 'naveen@sundarprecision.com', '+91 90001 66666', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_chennai, @role_manager, 'Geetha Krishnan', 'geetha@sundarprecision.com', '+91 90001 77777', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active'),
(@company_id, @branch_coimbatore, @role_manager, 'Ashok Reddy', 'ashok@sundarprecision.com', '+91 90001 88888', '$2b$12$3o1zJmYkYqQmA0z0oQ0m5.4l8kD5t8xnRk5m2yV4c1eXwQfJZzXhK', 'password', 0, 'active');

-- assign branch managers -------------------------------------------------
UPDATE branches SET manager_user_id = (SELECT id FROM users WHERE email='ravi@sundarprecision.com') WHERE id=@branch_chennai;
UPDATE branches SET manager_user_id = (SELECT id FROM users WHERE email='meena@sundarprecision.com') WHERE id=@branch_coimbatore;
UPDATE branches SET manager_user_id = (SELECT id FROM users WHERE email='arjun@sundarprecision.com') WHERE id=@branch_bengaluru;
UPDATE branches SET manager_user_id = (SELECT id FROM users WHERE email='priya@sundarprecision.com') WHERE id=@branch_hyderabad;

-- ROLE PERMISSIONS (Branch Manager grid exactly as in PDF) --------------
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_branch_mgr, id,
  CASE module_key WHEN 'hr_employee' THEN 0 WHEN 'company_settings' THEN 0 ELSE 1 END,
  CASE module_key WHEN 'sales_crm' THEN 1 WHEN 'inventory' THEN 1 WHEN 'purchase' THEN 1 WHEN 'service_desk' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'sales_crm' THEN 1 WHEN 'inventory' THEN 1 WHEN 'service_desk' THEN 1 ELSE 0 END,
  0,
  CASE module_key WHEN 'sales_crm' THEN 1 ELSE 0 END
FROM modules;

-- Owner: full access to everything
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_owner, id, 1, 1, 1, 1, 1 FROM modules;

-- Manager: all modules, no company settings
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_manager, id,
  CASE module_key WHEN 'company_settings' THEN 0 ELSE 1 END,
  CASE module_key WHEN 'company_settings' THEN 0 ELSE 1 END,
  CASE module_key WHEN 'company_settings' THEN 0 ELSE 1 END,
  0, 1
FROM modules;

-- Sales Staff: sales/CRM only
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_sales, id,
  CASE module_key WHEN 'dashboard' THEN 1 WHEN 'sales_crm' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'sales_crm' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'sales_crm' THEN 1 ELSE 0 END,
  0, 0
FROM modules;

-- Accountant
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_accountant, id,
  CASE module_key WHEN 'dashboard' THEN 1 WHEN 'finance_gst' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'finance_gst' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'finance_gst' THEN 1 ELSE 0 END,
  0, CASE module_key WHEN 'finance_gst' THEN 1 ELSE 0 END
FROM modules;

-- Production Staff
INSERT INTO role_permissions (role_id, module_id, can_view, can_add, can_edit, can_delete, can_approve)
SELECT @role_production, id,
  CASE module_key WHEN 'dashboard' THEN 1 WHEN 'manufacturing' THEN 1 WHEN 'inventory' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'manufacturing' THEN 1 WHEN 'inventory' THEN 1 ELSE 0 END,
  CASE module_key WHEN 'manufacturing' THEN 1 ELSE 0 END,
  0, 0
FROM modules;

-- DASHBOARD METRICS (today) ----------------------------------------------
INSERT INTO daily_metrics (company_id, metric_date, todays_sales, sales_change_pct, todays_purchase, purchase_change_pct, pending_payments, overdue_invoice_count, stock_alert_count, below_reorder_count)
VALUES (@company_id, '2026-07-07', 642800, 12.4, 218300, -4.1, 986200, 14, 7, 3);

-- PROFIT & LOSS (6 months) ------------------------------------------------
INSERT INTO profit_loss_monthly (company_id, month_label, month_order, revenue_lakhs, net_profit_lakhs) VALUES
(@company_id, 'Feb', 1, 32.0, 14.0),
(@company_id, 'Mar', 2, 34.5, 16.2),
(@company_id, 'Apr', 3, 33.8, 15.5),
(@company_id, 'May', 4, 36.2, 17.8),
(@company_id, 'Jun', 5, 38.0, 19.4),
(@company_id, 'Jul', 6, 40.1, 20.6);

-- PRODUCTION ORDERS --------------------------------------------------------
INSERT INTO production_orders (company_id, wo_number, product_name, units, stage, progress_pct) VALUES
(@company_id, 'WO-1042', 'Hex Bolt M8', 5000, 'Quality Checking', 78),
(@company_id, 'WO-1045', 'Flange Coupling', 1200, 'Machining', 42),
(@company_id, 'WO-1046', 'Bracket Type-A', 3000, 'Raw Material Prep', 15);

-- ATTENDANCE ----------------------------------------------------------------
INSERT INTO attendance_daily (company_id, attendance_date, present_count, on_leave_count, absent_count)
VALUES (@company_id, '2026-07-07', 42, 5, 3);

-- CUSTOMERS + DUES (follow-up list) ------------------------------------------
INSERT INTO customers (company_id, customer_name, customer_type, city, zone) VALUES
(@company_id, 'Om Traders', 'Retail', 'Bengaluru', NULL),
(@company_id, 'Shree Fasteners', 'Distributor', 'Coimbatore', NULL),
(@company_id, 'Vasan Autoparts', 'OEM', 'Chennai', NULL),
(@company_id, 'Lakshmi Hardware', 'Retail', 'Madurai', NULL),
(@company_id, 'Sri Ganesh Traders', 'Retail', 'Kolar', 'Kolar Retail Zone'),
(@company_id, 'New Balaji Stores', 'Retail', 'Kolar', 'Kolar Retail Zone'),
(@company_id, 'Kolar Hardware Mart', 'Retail', 'Kolar', 'Kolar Retail Zone');

INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 184500, 'overdue', 22, NULL, '2026-06-15' FROM customers WHERE customer_name='Om Traders';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 62000, 'due_soon', 0, NULL, '2026-07-10' FROM customers WHERE customer_name='Shree Fasteners';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 310200, 'overdue', 9, NULL, '2026-06-28' FROM customers WHERE customer_name='Vasan Autoparts';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 28750, 'received', 0, NULL, NULL FROM customers WHERE customer_name='Lakshmi Hardware';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 0, 'received', 0, 38, NULL FROM customers WHERE customer_name='Sri Ganesh Traders';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 0, 'received', 0, 33, NULL FROM customers WHERE customer_name='New Balaji Stores';
INSERT INTO customer_dues (customer_id, company_id, amount, status, days_overdue, last_order_days_ago, due_date)
SELECT id, @company_id, 142000, 'received', 0, 6, NULL FROM customers WHERE customer_name='Kolar Hardware Mart';

-- PRODUCTS (AI Assistant queries) ---------------------------------------------
INSERT INTO products (company_id, product_name, units_sold_month, change_pct, current_stock, daily_run_rate, supplier_price, reorder_suggested_units) VALUES
(@company_id, 'Hex Bolt M8 Series', 4820, 34.0, 2100, 161.5, 42.00, 500);

-- CONNECTED CHANNELS (AI Assistant panel) --------------------------------------
INSERT INTO connected_channels (company_id, channel_name, status) VALUES
(@company_id, 'WhatsApp Business', 'connected'),
(@company_id, 'Email', 'connected');

-- AI CONVERSATION SEED (matches PDF transcript) --------------------------------
INSERT INTO ai_conversations (company_id, user_id, title)
SELECT @company_id, id, 'This month sales lowest — tell me' FROM users WHERE email='ravi@sundarprecision.com';
SET @conv_id = LAST_INSERT_ID();

INSERT INTO ai_messages (conversation_id, sender, content) VALUES
(@conv_id, 'user', 'This month sales lowest — tell me'),
(@conv_id, 'assistant', 'Kolar Retail Zone has the lowest sales this month — ₹1,42,000, down 18% from last month. Two customers in that zone haven''t ordered in over 30 days.'),
(@conv_id, 'user', 'Which product is fast moving right now?'),
(@conv_id, 'assistant', 'Hex Bolt M8 Series is your fastest-moving product — 4,820 units sold this month, +34% over last month. At this pace, current stock (2,100 units) runs out in 13 days. Based on the trend, I''d suggest ordering around 500 units for next month at the current supplier price of ₹42/unit to stay ahead of demand.');
