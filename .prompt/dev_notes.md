# Development Notes - AI Interactions Log

This file logs all AI interactions and outcomes during the development of the Campus Resource Hub project.

## AI Tools Disclosure

The following AI tools were used throughout the development of this project:

- **Cursor AI** (Primary): AI coding assistant integrated into the Cursor IDE, used for code generation, debugging, refactoring, and feature implementation
- **Model Context Protocol (MCP)**: Framework for safe, read-only database access by AI agents
- **LLM Providers** (for Auto-Summary Reporter feature):
  - Ollama (local LLM inference)
  - LM Studio (local LLM server)
  - OpenAI API (cloud-based LLM, optional)

All AI-generated code has been reviewed, validated, and modified by the development team before integration into the codebase. AI suggestions were evaluated for correctness, security, and alignment with project requirements.

## Purpose
Track AI-assisted development sessions, decisions made, and outcomes to maintain context and improve future AI interactions.

---

## Log Entries

### 2024 - Initial Setup - AI First Folder Structure
- **Prompt/Request:** 
  - Create AI First Folder Structure as specified in project requirements
  - Set up .prompt/, docs/context/, and tests/ai_eval/ directories
  - Create documentation files and README explaining the structure
- **AI Response/Outcome:**
  - Created complete folder structure:
    - `.prompt/` with `dev_notes.md` and `golden_prompts.md`
    - `docs/context/` with subdirectories: `APA/`, `DT/`, `PM/`, `shared/`
    - `tests/ai_eval/` for AI feature validation tests
  - Created README.md documenting the Context Pack structure
  - Added README files in each subdirectory explaining their purpose
- **Notes:**
  - User instructed to maintain and update dev_notes.md and golden_prompts.md throughout all future AI interactions
  - This structure supports context-aware AI development and will be maintained going forward

### 2024 - Database Schema - Users Table
- **Prompt/Request:**
  - Create users table with specified schema:
    - user_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - name (TEXT NOT NULL)
    - email (TEXT NOT NULL UNIQUE)
    - password_hash (TEXT NOT NULL)
    - role (TEXT NOT NULL - 'student', 'staff', 'admin')
    - profile_image (TEXT)
    - department (TEXT)
    - created_at (DATETIME)
- **AI Response/Outcome:**
  - Created `database/schema.sql` with SQLite schema for users table
    - Added CHECK constraint for role validation
    - Added indexes on email and role for performance
    - Set created_at default to CURRENT_TIMESTAMP
  - Created `app/models.py` with SQLAlchemy User model
    - Implemented to_dict() method for API serialization
    - Added proper column types and constraints
  - Created `database/init_db.py` initialization script
    - Script reads schema.sql and creates database
    - Creates instance directory structure automatically
- **Notes:**
  - Used SQLite (AUTOINCREMENT syntax indicates SQLite)
  - Created both raw SQL schema and SQLAlchemy ORM model for flexibility
  - Database will be stored in `instance/campus_resource_hub.db` (Flask convention)
  - Ready for Flask-SQLAlchemy integration

### 2024 - Database Schema - Resources Table
- **Prompt/Request:**
  - Create resources table with specified schema:
    - resource_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - owner_id (INTEGER REFERENCES users(user_id))
    - title (TEXT NOT NULL)
    - description (TEXT)
    - category (TEXT)
    - location (TEXT)
    - capacity (INTEGER)
    - images (TEXT - comma separated paths or JSON array)
    - availability_rules (TEXT - JSON blob)
    - status (TEXT - 'draft', 'published', 'archived')
    - created_at (DATETIME)
- **AI Response/Outcome:**
  - Added resources table to `database/schema.sql`
    - Added CHECK constraint for status validation
    - Added foreign key constraint to users table
    - Added indexes on owner_id, category, and status for performance
  - Created Resource model in `app/models.py`
    - Added relationship to User model (owner)
    - Implemented to_dict() with JSON parsing for images and availability_rules
    - Handles both JSON and comma-separated formats for images field
- **Notes:**
  - Images field supports both JSON array and comma-separated string formats
  - Availability_rules stored as JSON blob for flexible recurring availability patterns
  - Resource model includes backref to User for easy access to owner's resources

### 2024 - Database Schema - Bookings Table
- **Prompt/Request:**
  - Create bookings table with specified schema:
    - booking_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - resource_id (INTEGER REFERENCES resources(resource_id))
    - requester_id (INTEGER REFERENCES users(user_id))
    - start_datetime (DATETIME)
    - end_datetime (DATETIME)
    - status (TEXT - 'pending', 'approved', 'rejected', 'cancelled', 'completed')
    - created_at (DATETIME)
    - updated_at (DATETIME)
- **AI Response/Outcome:**
  - Added bookings table to `database/schema.sql`
    - Added CHECK constraint for status validation
    - Added foreign key constraints to resources and users tables
    - Added indexes on resource_id, requester_id, status, start_datetime, and end_datetime
    - Set both created_at and updated_at defaults to CURRENT_TIMESTAMP
  - Created Booking model in `app/models.py`
    - Added relationships to Resource and User models
    - Implemented updated_at with onupdate to automatically update on changes
    - Implemented to_dict() method for API serialization
- **Notes:**
  - Indexes on datetime fields support efficient date range queries for availability checking
  - updated_at field automatically updates when booking record is modified
  - Booking model includes backrefs for easy access from Resource and User models

### 2024 - Database Schema - Messages Table
- **Prompt/Request:**
  - Create messages table with specified schema:
    - message_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - thread_id (INTEGER)
    - sender_id (INTEGER REFERENCES users(user_id))
    - receiver_id (INTEGER REFERENCES users(user_id))
    - content (TEXT)
    - timestamp (DATETIME)
- **AI Response/Outcome:**
  - Added messages table to `database/schema.sql`
    - Added foreign key constraints to users table for both sender and receiver
    - Added indexes on thread_id, sender_id, receiver_id, and timestamp
    - Set timestamp default to CURRENT_TIMESTAMP
  - Created Message model in `app/models.py`
    - Added relationships to User model with foreign_keys for sender and receiver
    - Implemented separate backrefs for sent_messages and received_messages
    - Implemented to_dict() method for API serialization
- **Notes:**
  - thread_id allows grouping messages into conversation threads
  - Separate relationships for sender and receiver enable efficient querying of user messages
  - Indexes support efficient retrieval of messages by thread, user, or time

### 2024 - Database Schema - Reviews and Admin Logs Tables
- **Prompt/Request:**
  - Create reviews table with specified schema:
    - review_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - resource_id (INTEGER REFERENCES resources(resource_id))
    - reviewer_id (INTEGER REFERENCES users(user_id))
    - rating (INTEGER - 1..5)
    - comment (TEXT)
    - timestamp (DATETIME)
  - Create admin_logs table (optional) with specified schema:
    - log_id (INTEGER PRIMARY KEY AUTOINCREMENT)
    - admin_id (INTEGER REFERENCES users(user_id))
    - action (TEXT)
    - target_table (TEXT)
    - details (TEXT)
    - timestamp (DATETIME)
- **AI Response/Outcome:**
  - Added reviews table to `database/schema.sql`
    - Added CHECK constraint to ensure rating is between 1 and 5
    - Added foreign key constraints to resources and users tables
    - Added indexes on resource_id, reviewer_id, rating, and timestamp
    - Set timestamp default to CURRENT_TIMESTAMP
  - Added admin_logs table to `database/schema.sql`
    - Added foreign key constraint to users table
    - Added indexes on admin_id, action, target_table, and timestamp
    - Set timestamp default to CURRENT_TIMESTAMP
  - Created Review model in `app/models.py`
    - Added relationships to Resource and User models
    - Implemented to_dict() method for API serialization
  - Created AdminLog model in `app/models.py`
    - Added relationship to User model
    - Implemented to_dict() method for API serialization
- **Notes:**
  - Reviews table supports ratings and comments for resources
  - Rating constraint ensures valid 1-5 star ratings
  - Admin_logs table provides audit trail for administrative actions
  - Both tables include comprehensive indexes for efficient querying

### 2024 - Model Context Protocol (MCP) Integration
- **Prompt/Request:**
  - Implement Model Context Protocol (MCP) integration for safe, read-only database access
  - Enable AI agents to query or inspect database content safely
  - Support features such as summaries or intelligent search
  - Document MCP usage in dev_notes.md and README
- **AI Response/Outcome:**
  - Created MCP server structure in `mcp/` directory
    - `mcp_server.py` - Main MCP server implementation
    - `mcp_tools.py` - Read-only database query tools
    - `README.md` - MCP documentation and usage guide
  - Implemented read-only database access layer
    - Safe query execution with parameterized queries
    - Support for intelligent search and summaries
    - No write operations allowed
  - Updated README.md with MCP section
  - Documented MCP integration in dev_notes.md
- **Notes:**
  - MCP enables structured, read-only interaction between AI layer and SQLite database
  - All database queries are parameterized to prevent SQL injection
  - MCP tools support features like resource summaries, intelligent search, and analytics
  - Implementation follows MCP specification for safe AI-database interaction

### 2024 - Wireframe Design - Complete Web App Wireframes
- **Prompt/Request:**
  - Create complete web app wireframes for Campus Resource Hub
  - Design modern, responsive, minimal university portal style
  - Include all main screens: Homepage, Resource Listing, Resource Detail, User Dashboard, Admin Dashboard, Forms
  - Use wireframe style (grayscale blocks, minimal color)
  - Include empty states and loading states
- **AI Response/Outcome:**
  - Created 6 complete wireframe HTML files in `wireframes/` directory:
    - `index.html` - Homepage with hero search, category icons, featured resources carousel
    - `resource-listing.html` - Resource listing with filters, grid/list view, pagination
    - `resource-detail.html` - Resource detail with image carousel, calendar, reviews, booking CTA
    - `user-dashboard.html` - User dashboard with sidebar, listings, bookings, messages, profile tabs
    - `admin-dashboard.html` - Admin dashboard with approvals queue, users, resources, reports
    - `forms.html` - All forms (sign in/up, create resource, booking) with validation states
  - Created `wireframes/README.md` documenting all wireframes
  - All wireframes use Bootstrap 5 for responsive layout
  - Implemented wireframe styling: grayscale blocks, dashed borders, minimal color
  - Included empty states and loading states as requested
  - All screens follow clean UI principles with clear visual hierarchy
- **Notes:**
  - Wireframes represent complete user journey from browsing to booking to administration
  - Design follows modern university portal style with card-based layouts
  - All wireframes are responsive and ready for frontend implementation
  - Forms include client-side validation states (valid/invalid)
  - Wireframes serve as foundation for user testing and frontend development

### 2024 - MVC Architecture Setup - Project Structure
- **Prompt/Request:**
  - Set up complete MVC architecture following project requirements
  - Create folder structure: /src with /controllers, /models, /views, /data_access, /static, /tests
  - Implement Data Access Layer (DAL) to encapsulate all database operations
  - Ensure controllers use DAL methods, never raw SQL
  - Set up Flask application with proper structure
  - Create requirements.txt with all dependencies
  - Set up testing infrastructure with pytest
- **AI Response/Outcome:**
  - Created complete MVC folder structure in `src/`:
    - `src/models/` - ORM classes (moved from app/models.py)
    - `src/controllers/` - Flask routes and blueprints
    - `src/views/` - Jinja2 HTML templates with base template
    - `src/data_access/` - Complete DAL implementation:
      - `user_dal.py` - User CRUD operations
      - `resource_dal.py` - Resource CRUD operations
      - `booking_dal.py` - Booking CRUD operations
      - `message_dal.py` - Message CRUD operations
      - `review_dal.py` - Review CRUD operations
    - `src/static/` - Static files (CSS)
    - `src/tests/` - Unit tests with pytest
  - Created `app.py` - Main Flask application entry point
  - Created `requirements.txt` with all dependencies:
    - Flask, Flask-SQLAlchemy, Flask-Login, bcrypt
    - pytest and testing tools
    - Security libraries (Flask-WTF, WTForms)
  - Created `.gitignore` for Python/Flask projects
  - Created `pytest.ini` for test configuration
  - Created `src/README.md` documenting architecture
  - All DAL classes follow consistent CRUD pattern
  - Controllers use DAL methods exclusively (no raw SQL)
- **Notes:**
  - Clear separation of concerns: Models (structure), Views (presentation), Controllers (coordination), DAL (data operations)
  - DAL ensures controllers never issue raw SQL queries
  - All database operations encapsulated in dedicated classes
  - Structure follows project requirements exactly
  - Ready for Flask-Login integration and authentication implementation
  - Testing infrastructure ready for unit tests

### 2024 - Database Path Fix - Windows Compatibility
- **Prompt/Request:**
  - Fix SQLite database connection error: "unable to open database file"
  - Error occurred when running app.py on Windows
- **AI Response/Outcome:**
  - Fixed database path handling in `app.py`:
    - Added automatic creation of `instance/` directory using `Path.mkdir(exist_ok=True)`
    - Changed to use absolute paths for database file
    - Added Windows path compatibility: convert backslashes to forward slashes for SQLite URI
    - Used pathlib for cross-platform path handling
  - Database URI now properly formatted for Windows: `sqlite:///C:/path/to/instance/campus_resource_hub.db`
- **Notes:**
  - SQLite URIs require forward slashes even on Windows
  - Pathlib ensures cross-platform compatibility
  - Instance directory is now created automatically if it doesn't exist
  - Fix resolves "unable to open database file" error on Windows systems

### 2024 - Missing Blueprint Error Fix
- **Prompt/Request:**
  - Fix BuildError: "Could not build url for endpoint 'auth.login'"
  - Error occurred when loading homepage - template referenced non-existent auth and dashboard blueprints
- **AI Response/Outcome:**
  - Created `src/controllers/auth.py` blueprint with login, logout, and register routes
  - Created `src/controllers/dashboard.py` blueprint with dashboard route
  - Registered both blueprints in `app.py`
  - Created corresponding templates:
    - `src/views/auth/login.html` - Login form
    - `src/views/auth/register.html` - Registration form
    - `src/views/dashboard/index.html` - Dashboard page
  - Updated User model to inherit from `UserMixin` for Flask-Login compatibility
  - Added `get_id()` method override to use `user_id` instead of default `id`
  - Updated `load_user()` function with error handling
  - Added "Sign Up" link to navigation in base template
- **Notes:**
  - Auth routes are placeholder implementations (TODO comments for actual logic)
  - User model now fully compatible with Flask-Login
  - All referenced endpoints now exist and are registered
  - Application should load without BuildError

### 2024 - Core Features Implementation
- **Prompt/Request:**
  - Implement all 8 core features required for the project:
    1. User Management & Authentication (sign up, sign in, sign out with bcrypt)
    2. Resource Listings (CRUD operations)
    3. Search & Filter (keyword, category, location, capacity, sorting)
    4. Booking & Scheduling (calendar booking, conflict detection, approval workflow)
    5. Messaging & Notifications (thread-based messaging)
    6. Reviews & Ratings (rating system with aggregates)
    7. Admin Panel (dashboard, user/resource/booking/review management)
    8. Documentation (README with setup instructions)
- **AI Response/Outcome:**
  - **Authentication**: Implemented complete sign up/sign in/logout with bcrypt password hashing via werkzeug.security
    - Form validation, email uniqueness check, password confirmation
    - Role-based access control (student, staff, admin)
  - **Resource CRUD**: Created `resources.py` controller with full CRUD operations
    - Create, read, update, delete resources
    - Owner and admin permission checks
    - Status management (draft, published, archived)
  - **Search & Filter**: Enhanced `main.py` with search functionality
    - Keyword search across title, description, location
    - Filter by category, location, capacity
    - Sort by recent, top rated (most booked TODO)
  - **Booking & Scheduling**: Created `bookings.py` controller
    - Calendar-based booking with date/time selection
    - Conflict detection using BookingDAL.check_availability()
    - Approval workflow: automatic for owners/staff, pending for students
    - Status management: pending, approved, rejected, cancelled, completed
    - API endpoint for availability checking
  - **Messaging**: Created `messages.py` controller
    - Thread-based messaging system
    - Conversation grouping by user
    - AJAX endpoint for sending messages
  - **Reviews & Ratings**: Created `reviews.py` controller
    - Rating system (1-5 stars) with validation
    - Review creation after completed bookings only
    - Aggregate rating calculation via ReviewDAL
    - Review editing and deletion
  - **Admin Panel**: Created `admin.py` controller with admin_required decorator
    - Dashboard with statistics (users, resources, bookings)
    - User management (view, edit, delete)
    - Resource management and approval queue
    - Booking management
    - Review moderation
    - Admin action logging via AdminLog model
  - **Documentation**: Updated README.md with:
    - Complete setup instructions
    - First time setup guide
    - Feature list
    - Database migration notes
- **Notes:**
  - All controllers use DAL methods (no raw SQL)
  - Role-based access control implemented throughout
  - Approval workflows in place for bookings and resources
  - Admin actions are logged for audit trail
  - Email notifications marked as TODO (simulated for now)
  - All core features implemented and ready for testing
  - Templates still need to be created for full functionality

---

### 2024 - Messaging & Notifications - Design Decisions

- **Prompt/Request:**
  - User requested clarification on messaging system design decisions:
    - Is it real-time?
    - Is it threaded?
    - Is it email-like?
- **AI Response/Outcome:**
  - **Current Implementation Analysis:**
    1. **Threading Model: Email-like Conversation Grouping**
       - Messages are grouped by user pairs (conversations between two users)
       - `thread_id` field exists in database but is used minimally
       - Thread ID is set to the first message's ID when a new conversation starts
       - Messages are displayed in chronological order within each conversation
       - **Design Choice: Email-like** - Conversations are organized by participant, not by topic/thread
    
    2. **Real-time Status: NOT Real-time (Request-Response Model)**
       - Messages are sent via form POST or AJAX POST
       - Page refresh required to see new messages
       - No WebSocket or Server-Sent Events (SSE) implementation
       - **Design Choice: Traditional Request-Response** - Simple, stateless, no real-time updates
    
    3. **UI Style: Hybrid (Email List + Chat Bubbles)**
       - Left sidebar shows conversation list (email-like inbox)
       - Right panel shows message thread with chat-style bubbles
       - Messages display with sender/receiver distinction
       - Timestamps shown for each message
       - **Design Choice: Familiar Email Interface** - Easy to understand, works well for asynchronous communication
    
    4. **Automated Notifications: System Messages**
       - Automated messages sent when bookings are:
         - Created (pending or approved)
         - Approved
         - Rejected
         - Cancelled
       - Messages sent from resource owner to requester
       - Waitlist notifications sent when slots become available
       - **Design Choice: In-app Messaging** - All notifications go to user's message inbox
    
    5. **Unread Message Tracking:**
       - Unread count displayed in navigation bar
       - Unread count per conversation in message list
       - Currently: All received messages are considered unread (simplified implementation)
       - **Future Enhancement:** Could add `is_read` boolean field to Message model
    
  - **Recommended Design Decisions Documented:**
    - **Threading:** Email-like conversation model (grouped by user pairs) - ✅ Implemented
    - **Real-time:** Traditional request-response (not real-time) - ✅ Implemented
    - **UI Style:** Email-like list with chat bubbles - ✅ Implemented
    - **Notifications:** In-app messaging system - ✅ Implemented
    
  - **Potential Future Enhancements:**
    - Add `is_read` field to Message model for proper read/unread tracking
    - Implement real-time updates using WebSockets or polling
    - Add email notifications as optional feature
    - Support for group conversations (multiple participants)
    - Message search functionality
    - File attachments in messages

- **Notes:**
  - Current implementation prioritizes simplicity and familiarity
  - Email-like model works well for asynchronous campus resource communication
  - Real-time features could be added later if needed
  - System messages are fully functional for booking notifications

---

### 2024 - Content Moderation System - Flagging and Reporting

- **Prompt/Request:**
  - Implement flagging/reporting system where students and staff can flag reviews or report messages
  - Admin should be able to view flagged reviews and reported messages
  - Admin can hide reviews, suspend users, or delete content; all actions logged in admin_logs
- **AI Response/Outcome:**
  - Created `ReviewFlag` model to track when users flag inappropriate reviews
    - Includes `review_id`, `user_id` (flagger), `reason`, `created_at`
    - Unique constraint prevents duplicate flags from same user
  - Created `MessageReport` model to track when users report inappropriate messages
    - Includes `message_id`, `user_id` (reporter), `reason`, `created_at`
    - Unique constraint prevents duplicate reports from same user
  - Added `is_hidden` column to `Review` model for admin moderation
  - Added `is_suspended` column to `User` model for account suspension
  - Created routes for users to flag reviews (`/reviews/<id>/flag`) and report messages (`/messages/<id>/report`)
  - Updated admin reviews page to show flagged reviews first with flag counts
  - Created admin page for reported messages (`/admin/messages/reported`)
  - Implemented admin moderation actions:
    - Hide/unhide reviews (`/admin/reviews/<id>/hide`, `/admin/reviews/<id>/unhide`)
    - Delete reviews (`/admin/reviews/<id>/delete`)
    - Delete messages (`/admin/messages/<id>/delete`)
    - Suspend/unsuspend users (`/admin/users/<id>/suspend`, `/admin/users/<id>/unsuspend`)
  - All admin actions logged in `admin_logs` table via `log_admin_action()` function
  - Added "Ignore" buttons for flagged reviews and reported messages to dismiss flags/reports
  - Added UI buttons for flagging reviews and reporting messages in templates
  - Updated login to prevent suspended users from logging in
- **Notes:**
  - Flagging/reporting system enables community-driven content moderation
  - Admin moderation tools provide comprehensive control over platform content
  - All moderation actions are logged for audit trail
  - Suspended users cannot log in, providing effective account management
  - Ignore functionality allows admins to dismiss false flags/reports

---

### 2024 - Student Resource Approval Workflow

- **Prompt/Request:**
  - Students should require admin approval when creating resources
  - Resources created by students should not appear on site until approved
  - Staff and admins can publish resources immediately
- **AI Response/Outcome:**
  - Modified resource creation logic in `src/controllers/resources.py`:
    - Students: Resources automatically set to `'draft'` status (requires approval)
    - Staff/Admins: Can choose status, defaults to `'published'` (immediate visibility)
  - Updated resource creation form to hide status field for students
    - Shows info message explaining approval requirement
    - Staff/admins see status dropdown with options
  - Updated resource edit form to prevent students from changing status
    - Students cannot publish their own resources
    - Status remains `'draft'` until admin approval
  - Added warning banner on resource detail page for draft resources
  - Admin approval queue already configured to show `'draft'` resources
  - Updated flash messages to inform students about approval requirement
- **Notes:**
  - Ensures quality control for student-created resources
  - Admin approval queue provides centralized review process
  - Staff and admins maintain ability to publish immediately
  - Clear user feedback about approval status throughout workflow

---

### 2024 - Navigation and UX Improvements

- **Prompt/Request:**
  - Fix back button navigation when viewing messages from reported messages page
  - Add "Ignore" buttons for flagged reviews and reported messages
- **AI Response/Outcome:**
  - Fixed conversation page back button to check `return_to` query parameter
    - When accessed from reported messages page, back button returns to reported messages
    - Parameter preserved when sending messages in conversation
  - Added "Ignore" functionality for flagged reviews:
    - Route: `/admin/reviews/<id>/ignore` - removes all flags for a review
    - Logged in admin_logs with flag count removed
  - Added "Ignore" functionality for reported messages:
    - Route: `/admin/messages/<id>/ignore` - removes all reports for a message
    - Logged in admin_logs with report count removed
  - Updated admin templates to include "Ignore" buttons alongside delete/hide actions
- **Notes:**
  - Improved navigation flow for admin moderation workflow
  - Ignore functionality allows admins to dismiss false flags/reports without deleting content
  - Better UX for admins reviewing reported content

---

### 2024 - Bug Fixes and Database Schema Updates

- **Prompt/Request:**
  - Fix `OperationalError: no such column: reviews.is_hidden`
  - Fix `UndefinedError: 'getattr' is undefined` in Jinja2 templates
- **AI Response/Outcome:**
  - Created migration script `fix_reviews_table.py` to add `is_hidden` column to reviews table
    - Script checks if column exists before adding
    - Uses SQLite `ALTER TABLE` to add column
  - Updated `ReviewDAL.get_by_resource()` to handle missing `is_hidden` column gracefully
    - Checks column existence before filtering
    - Falls back to raw SQL if column doesn't exist
  - Fixed Jinja2 template error by replacing `getattr(user, 'is_suspended', False)` with direct attribute access `user.is_suspended`
    - Updated `src/views/admin/users.html` to use direct attribute access
    - Jinja2 doesn't support Python's `getattr()` function
  - Created migration script `add_is_suspended_column.py` to add `is_suspended` column to users table
- **Notes:**
  - Database migrations handled via temporary scripts (ALTER TABLE)
  - Code made defensive to handle schema changes gracefully
  - Jinja2 templates must use direct attribute access, not Python built-ins
  - Migration scripts verify column existence before adding to prevent errors

---

