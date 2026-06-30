-- Migration: Make phone_no optional for users table
-- Date: 2026-06-30

-- Alter the users table to allow NULL values for phone_no
ALTER TABLE users ALTER COLUMN phone_no DROP NOT NULL;

-- Note: The UNIQUE constraint on phone_no will remain, 
-- ensuring that if a phone number is provided, it must be unique
