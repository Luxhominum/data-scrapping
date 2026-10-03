-- ==============================================================================
-- PGE Executive Sales Dashboard - Supabase Database Schema
-- Run this script in the Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)
-- ==============================================================================

-- 1. Create Sales Transactions Table
CREATE TABLE IF NOT EXISTS public.pge_sales_transactions (
    id BIGSERIAL PRIMARY KEY,
    year INT NOT NULL,
    month VARCHAR(7) NOT NULL,            -- e.g. '2023-01', '2026-08'
    platform VARCHAR(20) NOT NULL,        -- 'Shopee' or 'TikTok'
    product_name TEXT NOT NULL,
    variation TEXT DEFAULT '',
    revenue NUMERIC(15, 2) NOT NULL DEFAULT 0,
    quantity INT NOT NULL DEFAULT 1,
    orders INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Create High-Performance Analytical Indexes
CREATE INDEX IF NOT EXISTS idx_pge_sales_year_month 
    ON public.pge_sales_transactions (year, month);

CREATE INDEX IF NOT EXISTS idx_pge_sales_platform 
    ON public.pge_sales_transactions (platform);

CREATE INDEX IF NOT EXISTS idx_pge_sales_product_name 
    ON public.pge_sales_transactions (product_name);

CREATE INDEX IF NOT EXISTS idx_pge_sales_created_at 
    ON public.pge_sales_transactions (created_at DESC);

-- 3. Configure Row Level Security (RLS)
-- Enables public read-only access for the executive dashboard
ALTER TABLE public.pge_sales_transactions ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users (the frontend dashboard) to SELECT data
CREATE POLICY "Allow public read-only access for dashboard"
    ON public.pge_sales_transactions
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Allow inserting transactions only via authenticated backend or service_role
CREATE POLICY "Allow insert from authenticated or service_role"
    ON public.pge_sales_transactions
    FOR INSERT
    TO service_role, authenticated
    WITH CHECK (true);

-- 4. Enable Supabase Realtime Replication for Live Streaming
-- This allows the dashboard to receive WebSocket events whenever an order is inserted
ALTER PUBLICATION supabase_realtime ADD TABLE public.pge_sales_transactions;

-- 5. Optional Analytical View for Instant Aggregates
CREATE OR REPLACE VIEW public.v_pge_monthly_summary AS
SELECT
    year,
    month,
    platform,
    COUNT(*) AS total_skus,
    SUM(orders) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(revenue) AS total_revenue
FROM public.pge_sales_transactions
GROUP BY year, month, platform
ORDER BY year DESC, month DESC;
