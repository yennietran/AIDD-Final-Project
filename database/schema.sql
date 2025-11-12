-- Campus Resource Hub Database Schema
-- SQLite Database

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'staff', 'admin')),
    profile_image TEXT,
    department TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on role for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Resources Table
CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(user_id),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    location TEXT,
    capacity INTEGER,
    images TEXT,  -- comma separated paths or JSON array
    availability_rules TEXT,  -- JSON blob describing recurring availability
    status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_resources_owner_id ON resources(owner_id);
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id),
    requester_id INTEGER NOT NULL REFERENCES users(user_id),
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled', 'completed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_bookings_resource_id ON bookings(resource_id);
CREATE INDEX IF NOT EXISTS idx_bookings_requester_id ON bookings(requester_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_start_datetime ON bookings(start_datetime);
CREATE INDEX IF NOT EXISTS idx_bookings_end_datetime ON bookings(end_datetime);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER,
    sender_id INTEGER NOT NULL REFERENCES users(user_id),
    receiver_id INTEGER NOT NULL REFERENCES users(user_id),
    content TEXT,
    is_read INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id),
    reviewer_id INTEGER NOT NULL REFERENCES users(user_id),
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_reviews_resource_id ON reviews(resource_id);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer_id ON reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_timestamp ON reviews(timestamp);

-- Admin Logs Table (Optional)
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL REFERENCES users(user_id),
    action TEXT,
    target_table TEXT,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_action ON admin_logs(action);
CREATE INDEX IF NOT EXISTS idx_admin_logs_target_table ON admin_logs(target_table);
CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp);

-- Waitlist Table
CREATE TABLE IF NOT EXISTS waitlist (
    waitlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    requested_datetime DATETIME NOT NULL,
    notified_at DATETIME,
    status TEXT NOT NULL CHECK(status IN ('active', 'notified', 'converted', 'cancelled')) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_waitlist_resource_id ON waitlist(resource_id);
CREATE INDEX IF NOT EXISTS idx_waitlist_user_id ON waitlist(user_id);
CREATE INDEX IF NOT EXISTS idx_waitlist_status ON waitlist(status);
CREATE INDEX IF NOT EXISTS idx_waitlist_requested_datetime ON waitlist(requested_datetime);

