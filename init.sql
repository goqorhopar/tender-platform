-- Initialize database with required extensions and schemas

-- Create necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- Create indexes for text search if not exists
-- These will be created by SQLAlchemy but we can add them here for optimization
-- CREATE INDEX IF NOT EXISTS idx_tenders_search ON tenders USING gin(to_tsvector('russian', title || ' ' || description));
-- CREATE INDEX IF NOT EXISTS idx_suppliers_search ON suppliers USING gin(to_tsvector('russian', name || ' ' || specialization));

-- Add any custom functions or triggers if needed
-- Example: Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Example: Trigger to automatically update updated_at
-- This would be applied to tables as needed
-- CREATE TRIGGER update_tenders_updated_at BEFORE UPDATE ON tenders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add any initial data or seed data if needed
-- INSERT INTO users (id, email, full_name, role, is_active, is_email_verified, created_at, updated_at) 
-- VALUES (uuid_generate_v4(), 'admin@example.com', 'Admin User', 'admin', true, true, NOW(), NOW());