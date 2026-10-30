-- Disable foreign keys during table drops and creation
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS organizations;

PRAGMA foreign_keys = ON;

-- 1. Organizations (Enterprise Customers)
CREATE TABLE organizations (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    industry TEXT NOT NULL,
    tier TEXT CHECK(tier IN ('Startup', 'Growth', 'Enterprise')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Subscription Plans
CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    plan_name TEXT NOT NULL,
    monthly_rate_usd DECIMAL(10, 2) NOT NULL,
    max_seats INTEGER NOT NULL
);

-- 3. Customer Subscriptions
CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'past_due', 'canceled')) NOT NULL,
    current_period_start DATE NOT NULL,
    current_period_end DATE NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
);

-- 4. Invoices (Billing Records)
CREATE TABLE invoices (
    invoice_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    amount_usd DECIMAL(10, 2) NOT NULL,
    status TEXT CHECK(status IN ('paid', 'open', 'void', 'uncollectible')) NOT NULL,
    invoice_date DATE NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- 5. Invoice Items (Granular Line Items)
CREATE TABLE invoice_items (
    item_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_usd DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);

-- Indexes for performance
CREATE INDEX idx_org_country ON organizations(country);
CREATE INDEX idx_invoices_org_date ON invoices(org_id, invoice_date);
CREATE INDEX idx_invoices_status ON invoices(status);

-- Seed Data: Plans
INSERT INTO plans VALUES 
('plan_starter', 'Starter Tier', 49.00, 5),
('plan_growth', 'Growth Tier', 199.00, 20),
('plan_enterprise', 'Enterprise Tier', 999.00, 100);

-- Seed Data: Organizations
INSERT INTO organizations VALUES
('org_001', 'RazorMetrics India', 'India', 'Fintech', 'Enterprise', '2023-01-15 10:00:00'),
('org_002', 'Zephyr Logistics', 'India', 'Supply Chain', 'Growth', '2023-04-10 11:30:00'),
('org_003', 'Nordic Health Systems', 'Sweden', 'Healthcare', 'Enterprise', '2022-11-20 09:15:00'),
('org_004', 'Apex Cloud Labs', 'United States', 'SaaS', 'Enterprise', '2023-02-01 14:00:00'),
('org_005', 'Tokyo Digital Media', 'Japan', 'Media', 'Startup', '2024-01-05 08:45:00');

-- Seed Data: Subscriptions
INSERT INTO subscriptions VALUES
('sub_101', 'org_001', 'plan_enterprise', 'active', '2024-01-01', '2024-12-31'),
('sub_102', 'org_002', 'plan_growth', 'active', '2024-02-01', '2024-08-01'),
('sub_103', 'org_003', 'plan_enterprise', 'active', '2024-01-01', '2024-12-31'),
('sub_104', 'org_004', 'plan_enterprise', 'past_due', '2024-03-01', '2025-02-28'),
('sub_105', 'org_005', 'plan_starter', 'canceled', '2024-01-10', '2024-04-10');

-- Seed Data: Invoices
INSERT INTO invoices VALUES
('inv_501', 'org_001', 999.00, 'paid', '2024-01-01'),
('inv_502', 'org_001', 1499.00, 'paid', '2024-02-01'),
('inv_503', 'org_002', 199.00, 'paid', '2024-02-01'),
('inv_504', 'org_002', 199.00, 'paid', '2024-03-01'),
('inv_505', 'org_003', 999.00, 'paid', '2024-01-15'),
('inv_506', 'org_004', 999.00, 'open', '2024-03-01');

-- Seed Data: Line Items
INSERT INTO invoice_items VALUES
('item_01', 'inv_501', 'Enterprise Subscription Monthly Base', 1, 999.00),
('item_02', 'inv_502', 'Enterprise Subscription Monthly Base', 1, 999.00),
('item_03', 'inv_502', 'Additional 50 Seats Addon', 1, 500.00),
('item_04', 'inv_503', 'Growth Subscription Monthly Base', 1, 199.00),
('item_05', 'inv_504', 'Growth Subscription Monthly Base', 1, 199.00),
('item_06', 'inv_505', 'Enterprise Subscription Monthly Base', 1, 999.00),
('item_07', 'inv_506', 'Enterprise Subscription Monthly Base', 1, 999.00);