-- WeeFarm Database Setup Script
-- Run this as postgres user: psql -U postgres -f setup_database.sql

-- Create database
CREATE DATABASE weefarm_db;

-- Connect to the database
\c weefarm_db

-- Create user
CREATE USER weefarm_user WITH PASSWORD 'weefarm2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE weefarm_db TO weefarm_user;
GRANT ALL ON SCHEMA public TO weefarm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weefarm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weefarm_user;

-- Verify
SELECT current_database();
SELECT current_user;

-- Success message
\echo 'Database setup complete!'
\echo 'Database: weefarm_db'
\echo 'User: weefarm_user'
\echo 'Password: weefarm2024'
