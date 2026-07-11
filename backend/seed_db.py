"""
Run once after configuring .env and creating the MySQL database:

    python seed_db.py

This creates all tables (if not already created via database/schema.sql)
and inserts demo data identical to the PDF mockups, with real bcrypt
password hashes so you can log in immediately.

Demo login: prasannaranganathan.2001@gmail.com / Welcome@2026
"""
from datetime import date
from app.database import Base, engine, SessionLocal
from app import models
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

DEMO_PASSWORD = "Welcome@2026"

try:
    # if db.query(models.Company).count() > 0:
    #     print("Database already seeded. Exiting.")
    #     raise SystemExit(0)

    # ---------------- MODULES ----------------
    modules_data = [
        ("dashboard", "Dashboard", "main", 1, True),
        ("company_profile", "Company Profile", "login_setup", 2, True),
        ("branches", "Branches", "login_setup", 3, True),
        ("users", "Users", "login_setup", 4, True),
        ("roles_permissions", "Roles & Permissions", "login_setup", 5, True),
        ("sales_crm", "Sales + CRM", "workspace", 6, False),
        ("inventory", "Inventory", "workspace", 7, False),
        ("purchase", "Purchase", "workspace", 8, False),
        ("manufacturing", "Manufacturing", "workspace", 9, False),
        ("hr_employee", "HR & Employee", "workspace", 10, False),
        ("finance_gst", "Finance & GST", "workspace", 11, False),
        ("service_desk", "Service Desk", "workspace", 12, False),
        ("company_settings", "Company Settings", "login_setup", 13, True),
    ]
    modules = {}
    for key, name, cat, order, active in modules_data:
        m = models.Module(module_key=key, module_name=name, category=cat, sort_order=order, is_active=active)
        db.add(m)
        db.flush()
        modules[key] = m

    # ---------------- COMPANY ----------------
    company = models.Company(
        company_name="Sundar Precision Pvt Ltd",
        business_type="Private Limited Company",
        industry="Manufacturing — Precision Tooling",
        cin="U29100TN2015PTC098234",
        contact_number="+91 98410 22456",
        business_email="accounts@sundarprecision.com",
        address_line="Plot 14, SIDCO Industrial Estate, Ambattur",
        city="Chennai",
        state="Tamil Nadu",
        pin_code="600058",
        country="India",
        gstin="33AAECS1234F1Z5",
        pan="AAECS1234F",
        default_gst_rate=18.00,
        financial_year_start="April",
        plan_name="Business",
        plan_billing="billed annually",
        status="active",
        member_since=date(2022, 3, 1),
    )
    db.add(company)
    db.flush()

    # ---------------- ROLES ----------------
    role_defs = [
        ("Owner", "Full access to all modules and settings", "full", True),
        ("Manager", "Access to all modules, no billing/settings", "high", False),
        ("Branch Manager", "Manage assigned branch operations", "medium", False),
        ("Sales Staff", "Sales, CRM and quotations only", "limited", False),
        ("Accountant", "Finance, GST and payment modules", "limited", False),
        ("Production Staff", "Manufacturing and inventory only", "limited", False),
    ]
    roles = {}
    for name, desc, level, is_sys in role_defs:
        r = models.Role(company_id=company.id, role_name=name, description=desc,
                         access_level=level, is_system_role=is_sys)
        db.add(r)
        db.flush()
        roles[name] = r

    # Owner: full access everywhere
    for m in modules.values():
        db.add(models.RolePermission(role_id=roles["Owner"].id, module_id=m.id,
                                      can_view=True, can_add=True, can_edit=True,
                                      can_delete=True, can_approve=True))

    # Manager: all except company_settings
    for m in modules.values():
        allow = m.module_key != "company_settings"
        db.add(models.RolePermission(role_id=roles["Manager"].id, module_id=m.id,
                                      can_view=allow, can_add=allow, can_edit=allow,
                                      can_delete=False, can_approve=allow))

    # Branch Manager grid — exactly matches the PDF screenshot
    branch_mgr_grid = {
        "dashboard":      dict(v=1, a=0, e=0, d=0, ap=0),
        "sales_crm":      dict(v=1, a=1, e=1, d=0, ap=1),
        "inventory":      dict(v=1, a=1, e=1, d=0, ap=0),
        "purchase":       dict(v=1, a=1, e=0, d=0, ap=0),
        "manufacturing":  dict(v=1, a=0, e=0, d=0, ap=0),
        "hr_employee":    dict(v=0, a=0, e=0, d=0, ap=0),
        "finance_gst":    dict(v=1, a=0, e=0, d=0, ap=0),
        "service_desk":   dict(v=1, a=1, e=1, d=0, ap=0),
        "company_settings": dict(v=0, a=0, e=0, d=0, ap=0),
        "company_profile": dict(v=1, a=0, e=0, d=0, ap=0),
        "branches": dict(v=1, a=0, e=0, d=0, ap=0),
        "users": dict(v=1, a=0, e=0, d=0, ap=0),
        "roles_permissions": dict(v=0, a=0, e=0, d=0, ap=0),
    }
    for key, perm in branch_mgr_grid.items():
        m = modules[key]
        db.add(models.RolePermission(role_id=roles["Branch Manager"].id, module_id=m.id,
                                      can_view=bool(perm["v"]), can_add=bool(perm["a"]),
                                      can_edit=bool(perm["e"]), can_delete=bool(perm["d"]),
                                      can_approve=bool(perm["ap"])))

    # Sales Staff
    for m in modules.values():
        allow = m.module_key in ("dashboard", "sales_crm")
        edit_allow = m.module_key == "sales_crm"
        db.add(models.RolePermission(role_id=roles["Sales Staff"].id, module_id=m.id,
                                      can_view=allow, can_add=edit_allow, can_edit=edit_allow,
                                      can_delete=False, can_approve=False))

    # Accountant
    for m in modules.values():
        allow = m.module_key in ("dashboard", "finance_gst")
        edit_allow = m.module_key == "finance_gst"
        db.add(models.RolePermission(role_id=roles["Accountant"].id, module_id=m.id,
                                      can_view=allow, can_add=edit_allow, can_edit=edit_allow,
                                      can_delete=False, can_approve=edit_allow))

    # Production Staff
    for m in modules.values():
        allow = m.module_key in ("dashboard", "manufacturing", "inventory")
        edit_allow = m.module_key in ("manufacturing", "inventory")
        db.add(models.RolePermission(role_id=roles["Production Staff"].id, module_id=m.id,
                                      can_view=allow, can_add=edit_allow, can_edit=(m.module_key == "manufacturing"),
                                      can_delete=False, can_approve=False))

    db.flush()

    # ---------------- BRANCHES ----------------
    branch_defs = [
        ("Chennai HQ (Head Office)", "Head Office", "Plot 14, SIDCO Industrial Estate, Ambattur", "Chennai", "Tamil Nadu", "active", True),
        ("Coimbatore Plant", "Plant", "44/2, SIPCOT Industrial Park, Coimbatore", "Coimbatore", "Tamil Nadu", "active", False),
        ("Bengaluru Sales Office", "Sales Office", "No.9, Residency Road, Bengaluru", "Bengaluru", "Karnataka", "active", False),
        ("Hyderabad Depot", "Depot", "Plot 7, Kukatpally Industrial Area", "Hyderabad", "Telangana", "inactive", False),
    ]
    branches = {}
    for name, btype, addr, city, state, status, is_default in branch_defs:
        b = models.Branch(company_id=company.id, branch_name=name, branch_type=btype,
                           address=addr, city=city, state=state, status=status, is_default=is_default)
        db.add(b)
        db.flush()
        branches[name] = b

    # ---------------- USERS ----------------
    pw_hash = hash_password(DEMO_PASSWORD)
    user_defs = [
        ("Prasanna Ranganathan", "prasannaranganathan.2001@gmail.com", "+91 98410 22456", "Chennai HQ (Head Office)", "Owner", True, "active", "password"),
        # ("Meena Iyer", "prasannaranganathan.2001@gmail.com", "+91 90000 11111", "Coimbatore Plant", "Manager", False, "active", "password"),
    #     ("Arjun Das", "arjun@sundarprecision.com", "+91 90000 22222", "Bengaluru Sales Office", "Sales Staff", False, "active", "password"),
    #     ("Priya Reddy", "priya@sundarprecision.com", "+91 90000 33333", "Hyderabad Depot", "Branch Manager", False, "invited", "email_invite"),
    #     ("Karthik S", "karthik@sundarprecision.com", "+91 90000 44444", "Chennai HQ (Head Office)", "Accountant", False, "active", "password"),
    #     ("Divya Menon", "divya@sundarprecision.com", "+91 90000 55555", "Coimbatore Plant", "Production Staff", False, "suspended", "password"),
    #     ("Deepak Nair", "deepak@sundarprecision.com", "+91 90000 66666", "Chennai HQ (Head Office)", "Sales Staff", False, "active", "password"),
    #     ("Sneha Rao", "sneha@sundarprecision.com", "+91 90000 77777", "Chennai HQ (Head Office)", "Sales Staff", False, "active", "password"),
    #     ("Farhan Sheikh", "farhan@sundarprecision.com", "+91 90000 88888", "Bengaluru Sales Office", "Sales Staff", False, "active", "password"),
    #     ("Anita George", "anita@sundarprecision.com", "+91 90000 99999", "Coimbatore Plant", "Sales Staff", False, "active", "password"),
    #     ("Vikram Shah", "vikram@sundarprecision.com", "+91 90001 11111", "Bengaluru Sales Office", "Sales Staff", False, "active", "password"),
    #     ("Lakshmi Prasad", "lakshmi@sundarprecision.com", "+91 90001 22222", "Chennai HQ (Head Office)", "Accountant", False, "active", "password"),
    #     ("Suresh Babu", "suresh@sundarprecision.com", "+91 90001 33333", "Coimbatore Plant", "Production Staff", False, "active", "password"),
    #     ("Ramesh Pillai", "ramesh@sundarprecision.com", "+91 90001 44444", "Coimbatore Plant", "Branch Manager", False, "active", "password"),
    #     ("Kavya Menon", "kavya@sundarprecision.com", "+91 90001 55555", "Bengaluru Sales Office", "Branch Manager", False, "active", "password"),
    #     ("Naveen Kumar", "naveen@sundarprecision.com", "+91 90001 66666", "Hyderabad Depot", "Branch Manager", False, "active", "password"),
    #     ("Geetha Krishnan", "geetha@sundarprecision.com", "+91 90001 77777", "Chennai HQ (Head Office)", "Manager", False, "active", "password"),
    #     ("Ashok Reddy", "ashok@sundarprecision.com", "+91 90001 88888", "Coimbatore Plant", "Manager", False, "active", "password"),
    ]
    users = {}
    for name, email, mobile, branch_name, role_name, is_owner, status, login_method in user_defs:
        u = models.User(
            company_id=company.id,
            branch_id=branches[branch_name].id,
            role_id=roles[role_name].id,
            full_name=name,
            email=email,
            mobile_number=mobile,
            password_hash=pw_hash if login_method == "password" else None,
            login_method=login_method,
            is_owner=is_owner,
            status=status,
        )
        db.add(u)
        db.flush()
        users[email] = u

    branches["Chennai HQ (Head Office)"].manager_user_id = users["prasannaranganathan.2001@gmail.com"].id
    branches["Coimbatore Plant"].manager_user_id = users["prasannaranganathan.2001@gmail.com"].id
    branches["Bengaluru Sales Office"].manager_user_id = users["prasannaranganathan.2001@gmail.com"].id
    branches["Hyderabad Depot"].manager_user_id = users["prasannaranganathan.2001@gmail.com"].id

    # ---------------- DASHBOARD DATA ----------------
    db.add(models.DailyMetric(
        company_id=company.id, metric_date=date(2026, 7, 7),
        todays_sales=642800, sales_change_pct=12.4,
        todays_purchase=218300, purchase_change_pct=-4.1,
        pending_payments=986200, overdue_invoice_count=14,
        stock_alert_count=7, below_reorder_count=3,
    ))

    pl_data = [("Feb", 1, 32.0, 14.0), ("Mar", 2, 34.5, 16.2), ("Apr", 3, 33.8, 15.5),
               ("May", 4, 36.2, 17.8), ("Jun", 5, 38.0, 19.4), ("Jul", 6, 40.1, 20.6)]
    for label, order, rev, profit in pl_data:
        db.add(models.ProfitLossMonthly(company_id=company.id, month_label=label, month_order=order,
                                         revenue_lakhs=rev, net_profit_lakhs=profit))

    prod_orders = [
        ("WO-1042", "Hex Bolt M8", 5000, "Quality Checking", 78),
        ("WO-1045", "Flange Coupling", 1200, "Machining", 42),
        ("WO-1046", "Bracket Type-A", 3000, "Raw Material Prep", 15),
    ]
    for wo, name, units, stage, pct in prod_orders:
        db.add(models.ProductionOrder(company_id=company.id, wo_number=wo, product_name=name,
                                       units=units, stage=stage, progress_pct=pct))

    db.add(models.AttendanceDaily(company_id=company.id, attendance_date=date(2026, 7, 7),
                                   present_count=42, on_leave_count=5, absent_count=3))

    # ---------------- CUSTOMERS + DUES ----------------
    cust_defs = [
        ("Om Traders", "Retail", "Bengaluru", None),
        ("Shree Fasteners", "Distributor", "Coimbatore", None),
        ("Vasan Autoparts", "OEM", "Chennai", None),
        ("Lakshmi Hardware", "Retail", "Madurai", None),
        ("Sri Ganesh Traders", "Retail", "Kolar", "Kolar Retail Zone"),
        ("New Balaji Stores", "Retail", "Kolar", "Kolar Retail Zone"),
        ("Kolar Hardware Mart", "Retail", "Kolar", "Kolar Retail Zone"),
    ]
    customers = {}
    for name, ctype, city, zone in cust_defs:
        c = models.Customer(company_id=company.id, customer_name=name, customer_type=ctype, city=city, zone=zone)
        db.add(c)
        db.flush()
        customers[name] = c

    due_defs = [
        ("Om Traders", 184500, "overdue", 22, None),
        ("Shree Fasteners", 62000, "due_soon", 0, None),
        ("Vasan Autoparts", 310200, "overdue", 9, None),
        ("Lakshmi Hardware", 28750, "received", 0, None),
        ("Sri Ganesh Traders", 0, "received", 0, 38),
        ("New Balaji Stores", 0, "received", 0, 33),
        ("Kolar Hardware Mart", 142000, "received", 0, 6),
    ]
    for name, amount, status, overdue_days, last_order in due_defs:
        db.add(models.CustomerDue(customer_id=customers[name].id, company_id=company.id, amount=amount,
                                   status=status, days_overdue=overdue_days, last_order_days_ago=last_order))

    # ---------------- PRODUCTS ----------------
    db.add(models.Product(
        company_id=company.id, product_name="Hex Bolt M8 Series", units_sold_month=4820,
        change_pct=34.0, current_stock=2100, daily_run_rate=161.5,
        supplier_price=42.00, reorder_suggested_units=500,
    ))

    # ---------------- CONNECTED CHANNELS ----------------
    db.add(models.ConnectedChannel(company_id=company.id, channel_name="WhatsApp Business", status="connected"))
    db.add(models.ConnectedChannel(company_id=company.id, channel_name="Email", status="connected"))

    # ---------------- AI CONVERSATION SEED ----------------
    conv = models.AiConversation(company_id=company.id, user_id=users["prasannaranganathan.2001@gmail.com"].id,
                                  title="This month sales lowest — tell me")
    db.add(conv)
    db.flush()
    db.add(models.AiMessage(conversation_id=conv.id, sender="user", content="This month sales lowest — tell me"))
    db.add(models.AiMessage(conversation_id=conv.id, sender="assistant",
        content=("Kolar Retail Zone has the lowest sales this month — ₹1,42,000, down 18% from last month. "
                 "Two customers in that zone haven't ordered in over 30 days.")))
    db.add(models.AiMessage(conversation_id=conv.id, sender="user", content="Which product is fast moving right now?"))
    db.add(models.AiMessage(conversation_id=conv.id, sender="assistant",
        content=("Hex Bolt M8 Series is your fastest-moving product — 4,820 units sold this month, +34% over "
                 "last month. At this pace, current stock (2,100 units) runs out in 13 days. Based on the trend, "
                 "I'd suggest ordering around 500 units for next month at the current supplier price of ₹42/unit "
                 "to stay ahead of demand.")))

    db.commit()
    print("Database seeded successfully.")
    print(f"Login with: prasannaranganathan.2001@gmail.com / {DEMO_PASSWORD}")

except Exception as exc:
    db.rollback()
    print(f"Seeding failed: {exc}")
    raise
finally:
    db.close()
