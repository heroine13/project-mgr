-- Initialize database for Project Management System
CREATE DATABASE IF NOT EXISTS project_mgr;
USE project_mgr;

-- Set default character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET COLLATION_CONNECTION = 'utf8mb4_unicode_ci';

-- Create user with all privileges on this database
GRANT ALL PRIVILEGES ON project_mgr.* TO 'project_user'@'%';
FLUSH PRIVILEGES;