# Campus Resource Hub

A full-stack web application enabling university departments, student organizations, and individuals to list, share, and reserve campus resources.

## Project Overview

The Campus Resource Hub supports:
- Resource listing and sharing (study rooms, AV equipment, lab instruments, event spaces, tutoring time, etc.)
- Search and booking with calendar integration
- Role-based access control (student, staff, admin)
- Ratings and reviews
- Administrative workflows for approval and conflict resolution

## Tech Stack

- **Backend:** Python 3.10+ with Flask
- **Database:** SQLite (local development), PostgreSQL (optional for deployment)
- **Frontend:** Jinja2 templates + Bootstrap 5 (designed from Figma wireframes)
- **Authentication:** Flask-Login + bcrypt for password hashing
- **Testing:** pytest for unit tests
- **Version Control:** GitHub (branching, PRs required)
- **AI Integration:** Model Context Protocol (MCP) for safe database access

## Project Structure

```
.
├── src/                    # Main application source code (MVC architecture)
│   ├── controllers/        # Flask routes and blueprints (Controller Layer)
│   ├── models/             # ORM classes and database models (Model Layer)
│   ├── views/              # HTML/Jinja templates (View Layer)
│   ├── data_access/        # Encapsulated CRUD operations (Data Access Layer)
│   ├── static/             # Static files (CSS, JS, images)
│   └── tests/              # Unit tests for business logic
├── database/               # Database schema and initialization
├── mcp/                    # Model Context Protocol implementation
├── docs/                   # Documentation and context
│   └── context/            # Context Pack for AI-assisted development
│       ├── APA/            # Agility, Processes & Automation artifacts
│       ├── DT/             # Design Thinking artifacts
│       ├── PM/             # Product Management materials
│       └── shared/         # Common items
├── .prompt/                # AI development logs
│   ├── dev_notes.md        # Log of all AI interactions
│   └── golden_prompts.md   # High-impact prompts and responses
├── tests/                  # Additional tests
│   └── ai_eval/            # AI feature validation tests
├── additional deliverables/ # Project deliverables (PRD, ERD, slide deck, reflection)
├── app.py                  # Main Flask application entry point
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── API.md                  # API documentation
└── AI_SUMMARY_REPORTER.md  # AI Summary Reporter feature documentation
```

## Design Process

The frontend design was developed using a structured design process:

1. **Wireframing**: Initial wireframes were created in Figma to establish layout, user flows, and component structure
2. **Implementation**: The Figma wireframes served as the design foundation for building the HTML/Jinja2 templates
3. **Styling**: Bootstrap 5 was used to implement the visual design, ensuring responsive layouts and consistent UI components

Wireframe artifacts (PNG images) are stored in `docs/context/DT/` as part of the Design Thinking context pack.

## Architecture

The application follows a **Model-View-Controller (MVC)** pattern with clear separation of concerns:

- **Model Layer** (`src/models/`): SQLAlchemy ORM models defining database structure
- **View Layer** (`src/views/`): Jinja2 HTML templates for presentation
- **Controller Layer** (`src/controllers/`): Flask routes coordinating requests/responses
- **Data Access Layer** (`src/data_access/`): Encapsulated CRUD operations (controllers never issue raw SQL)

## AI First Folder Structure

This repository follows an AI-first development approach with a context-aware folder structure designed to help AI tools understand the project's architecture and generate accurate, contextually relevant code.

### Context Pack

The folder system collectively forms the **Context Pack**, a lightweight structure designed to help AI tools ground their reasoning in the project's goals, data, and user context.

## Model Context Protocol (MCP) Integration

This project implements **Model Context Protocol (MCP)** to enable safe, read-only interaction between AI agents and the SQLite database. MCP allows AI tools to query and inspect database content for features such as:

- **Intelligent Search**: AI-powered resource discovery and recommendations
- **Summaries**: Automated generation of resource summaries and analytics
- **Data Insights**: Safe querying for reporting and analysis

### MCP Features

- **Read-Only Access**: All database interactions are strictly read-only
- **Parameterized Queries**: SQL injection protection through parameterized queries
- **Structured Responses**: Consistent JSON responses for AI consumption
- **Safe Query Execution**: Query validation and error handling

All MCP interactions are logged and documented in `.prompt/dev_notes.md`.

## AI Collaboration Insights

This project has been developed with extensive AI assistance, primarily through Cursor's AI coding assistant. The collaboration has proven highly effective for rapid feature development, debugging, and code quality improvements. Key insights from this AI-assisted workflow include:

**Effective Prompting Strategies**: The most successful interactions occurred when prompts clearly specified requirements, user roles, and expected behaviors. For example, prompts that explicitly stated "students and staff can flag reviews, admin can hide/suspend/delete" generated complete, working implementations faster than vague requests.

**Iterative Refinement**: AI-generated code often required team review and modification, particularly for business logic validation and edge case handling. The AI excelled at generating boilerplate code, database models, and route structures, while human review ensured alignment with project requirements and security best practices.

**Context-Aware Development**: Maintaining `.prompt/dev_notes.md` and `golden_prompts.md` created a knowledge base that improved AI responses over time. The AI could reference previous solutions and patterns, leading to more consistent code generation.

**Feature Implementation**: Major features like the Auto-Summary Reporter, content moderation system, and role-based resource approval workflows were AI-suggested and implemented with significant time savings. The AI's ability to generate complete MVC implementations (models, controllers, views) in a single interaction accelerated development cycles.

**Challenges and Solutions**: The AI occasionally generated code that required database migrations or used patterns inconsistent with the project's architecture. These issues were resolved through iterative feedback, with the AI learning project-specific constraints and preferences.

Overall, AI assistance has been instrumental in maintaining development velocity while ensuring code quality through human oversight and review processes.

### Ethical Implications of AI Collaboration

The use of AI tools in this project raises several important ethical considerations that we have addressed transparently:

**Transparency and Attribution**: All AI-generated or AI-suggested code is clearly marked with attribution comments (e.g., "AI Contribution: ...") to maintain transparency about the development process. This ensures that reviewers and future maintainers understand which portions of the codebase were AI-assisted.

**Academic Integrity**: We have maintained strict adherence to academic integrity policies by:
- Disclosing all AI tools used (documented in `.prompt/dev_notes.md`)
- Reviewing and validating all AI-generated code before integration
- Ensuring no unreviewed AI outputs were submitted as final work
- Maintaining human oversight throughout the development process

**Code Quality and Responsibility**: While AI tools accelerated development, the development team maintained full responsibility for:
- Verifying correctness of AI-generated code
- Ensuring security best practices (SQL injection prevention, XSS protection, etc.)
- Validating business logic and edge cases
- Testing all AI-suggested features before deployment

**Knowledge and Learning**: The AI collaboration served as a learning tool, helping the team understand patterns, best practices, and alternative approaches. However, all final decisions and implementations reflect human judgment and project requirements.

**Bias and Fairness**: We recognize that AI tools may reflect biases present in their training data. To mitigate this, we:
- Reviewed all AI suggestions for potential bias (e.g., in user interface design, access control logic)
- Ensured diverse perspectives in code review processes
- Validated that features work equitably for all user roles (students, staff, admins)

This ethical framework ensures that AI assistance enhances rather than replaces human judgment, maintaining the integrity and quality of the final deliverable.

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd campus-resource-hub
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python database/init_db.py
```

   Alternatively, the database will be created automatically when you run the app for the first time.

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### First Time Setup

1. **Create an Admin Account**: 
   - Visit `/register` to create your first account
   - **Note:** All new accounts default to "Student" role
   - To get Admin access, create the account and then request a role change from your dashboard
   - Alternatively, you can manually update your role in the database if needed for initial setup

2. **Create Test Resources**:
   - Log in and visit `/resources/create` to add resources
   - **Students:** Resources are automatically set to "draft" and require admin approval
   - **Staff/Admins:** Can publish resources immediately
   - Published resources are visible to all users

3. **Test Booking Flow**:
   - Browse resources at `/resources`
   - Click on a resource to view details
   - Click "Book Now" to create a booking
   - Bookings may require approval depending on resource settings
   - If a time slot is unavailable, you can join the waitlist

## Core Features

### ✅ User Management & Authentication
- Sign up, sign in, sign out with email + password
- Passwords stored with bcrypt hashing
- Role-based access: Student, Staff, Admin
- **Role Change Requests:** Students can request Staff or Admin access; admins approve/deny requests
- **Account Security:** Admin can suspend/unsuspend users

### ✅ Resource Listings
- Full CRUD operations for resources
- Fields: title, description, images, category, location, availability rules, capacity
- Lifecycle: draft → published → archived
- **Requires Approval Flag:** Resources can be marked to require booking approval
- **Role-Based Publishing:** Students' resources require admin approval; Staff/Admins can publish immediately
- Visual availability calendar showing available days and time slots

### ✅ Search & Filter
- Keyword search across resources
- Filter by category, location, capacity
- Sort by: recent, most booked, top rated

### ✅ Booking & Scheduling
- Calendar-based booking with start/end time
- Visual calendar showing available/unavailable days and time slots
- Conflict detection to prevent double-booking
- Approval workflow: automatic or staff/admin approval
- Booking statuses: pending, approved, rejected, cancelled, completed
- **Waitlist Feature:** Join waitlist for fully booked resources; automatic notifications when slots open
- Same-day booking support with 15-minute buffer

### ✅ Messaging & Notifications
- Thread-based messaging between users
- Message threads grouped by conversation partner
- Real-time messaging support (AJAX endpoints)
- Automated notifications for booking approvals/rejections
- **Content Moderation:** Users can report inappropriate messages
- Admin can delete reported messages
- Read/unread message tracking

### ✅ Reviews & Ratings
- Users can rate resources (1-5 stars) after completed bookings
- Aggregate rating calculation
- Review moderation by admins
- **Content Moderation:** Users can flag inappropriate reviews
- Admin can hide, unhide, or delete reviews
- Review preview (first 3) with "View All Reviews" option

### ✅ Admin Panel
- Dashboard with statistics and recent activity
- User management (view, edit, delete, suspend/unsuspend)
- Resource management and approval queue (approve/reject pending resources)
- Booking management and approvals
- Review moderation (hide, unhide, delete, ignore flags)
- Message moderation (delete, ignore reports)
- **Role Change Requests:** View and approve/deny student requests for Staff/Admin access
- **AI Summary Report:** AI-powered system analytics and insights
- Admin action logging (all actions tracked in admin_logs)

### ✅ RESTful API
- Complete API endpoints for all features
- JSON request/response format
- Authentication via Flask-Login sessions
- Comprehensive API documentation (see `API.md`)

### ✅ Advanced Features
- **Waitlist System:** Join waitlist for fully booked resources with automatic notifications
- **Content Moderation:** Flag reviews and report messages; admin moderation tools
- **Role Change Requests:** Students can request role upgrades; admin approval workflow
- **AI Summary Reporter:** AI-powered system analytics using LLMs (Ollama, LM Studio, OpenAI)
- **Visual Calendar:** Day availability calendar showing available/unavailable days and slot counts
- **Availability Rules:** Set specific days/times when resources are available
- **Same-Day Booking:** Support for booking resources on the current day (with 15-minute buffer)

## Database Migration

The application uses SQLite for local development. Database tables are created automatically using SQLAlchemy's `db.create_all()`.

To reset the database:
1. Delete `instance/campus_resource_hub.db`
2. Restart the application (tables will be recreated)

For production deployment with PostgreSQL:
1. Set `DATABASE_URL` environment variable
2. The application will automatically use PostgreSQL instead of SQLite

## Testing & Validation

The project includes comprehensive test coverage for all core functionality, security, and integration scenarios. All tests use `pytest` and run against an in-memory SQLite database for isolation and speed.

### Test Requirements Coverage

✅ **Unit Tests for Booking Logic**
- Conflict detection (overlapping bookings, adjacent bookings, contained bookings)
- Status transitions (pending → approved, approved → cancelled, pending → rejected)
- Availability validation within resource hours

✅ **Data Access Layer (DAL) Tests**
- CRUD operations verified independently from Flask routes
- Tests for `BookingDAL`, `UserDAL`, and other DAL classes
- Ensures database operations work correctly at the data layer

✅ **Integration Tests**
- Complete authentication flow: register → login → access protected route
- Duplicate email registration prevention
- Invalid credentials handling
- Logout functionality
- Protected route access control

✅ **End-to-End Tests**
- Full booking flow: login → view resource → book resource → view booking
- Conflict detection in booking flow
- UI interaction simulation

✅ **Security Tests**
- SQL injection protection (parameterized queries)
- XSS protection (template escaping)
- CSRF protection configuration
- Input sanitization

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest src/tests/test_booking_logic.py
pytest src/tests/test_booking_dal.py
pytest src/tests/test_auth_integration.py
pytest src/tests/test_security.py
pytest src/tests/test_booking_e2e.py
```

**Run tests with coverage report:**
```bash
pytest --cov=src --cov-report=html
```

**Run tests matching a pattern:**
```bash
pytest -k "conflict"  # Run all tests with "conflict" in the name
pytest -k "auth"      # Run all authentication-related tests
```

### Test Structure

```
src/tests/
├── conftest.py              # Pytest fixtures (app, client, sample data)
├── test_booking_logic.py     # Unit tests for booking conflict detection & status transitions
├── test_booking_dal.py       # DAL CRUD operations for bookings
├── test_user_dal.py          # DAL CRUD operations for users
├── test_auth_integration.py  # Integration tests for auth flow
├── test_booking_e2e.py       # End-to-end booking scenario tests
└── test_security.py          # Security tests (SQL injection, XSS, CSRF)
```

### Test Configuration

Tests are configured in `pytest.ini`:
- Test paths: `src/tests`
- Test discovery: Files matching `test_*.py`
- Test isolation: Each test runs with a fresh in-memory database
- CSRF disabled: For easier testing (enabled in production)

### Writing New Tests

When adding new features, follow these patterns:

1. **Unit Tests**: Test business logic in isolation
   ```python
   def test_feature_name(app, sample_user):
       with app.app_context():
           # Test implementation
           assert result == expected
   ```

2. **DAL Tests**: Test data access layer independently
   ```python
   def test_dal_operation(app, sample_resource):
       with app.app_context():
           result = DALClass.create(...)
           assert result is not None
   ```

3. **Integration Tests**: Test full request/response flow
   ```python
   def test_feature_flow(client, app):
       response = client.post('/endpoint', data={...})
       assert response.status_code == 200
   ```

### Test Fixtures

Common fixtures available in `conftest.py`:
- `app`: Flask application with test configuration
- `client`: Test client for making HTTP requests
- `sample_user`: Test user (student role)
- `sample_staff`: Test staff user
- `sample_admin`: Test admin user
- `sample_resource`: Test resource with availability rules

### Security Testing

All security tests verify:
- **SQL Injection**: Parameterized queries prevent SQL injection attacks
- **XSS Protection**: Template auto-escaping prevents script injection
- **CSRF Protection**: CSRF tokens required for state-changing operations (in production)

### Continuous Integration

Tests should pass before merging any pull request. Run the full test suite:
```bash
pytest -v --tb=short
```

Expected output: All tests pass with no errors or warnings.

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

### Test Structure

The test suite includes:

#### 1. **Unit Tests - Data Access Layer (DAL)**
- `test_user_dal.py` - User CRUD operations
- `test_booking_dal.py` - Booking CRUD operations
- Tests verify DAL methods work independently from Flask routes

#### 2. **Unit Tests - Booking Logic**
- `test_booking_logic.py` - Conflict detection and status transitions
- Tests for overlapping bookings, adjacent bookings, different days
- Tests for status transitions (pending → approved, approved → cancelled, etc.)
- Tests for availability rules validation

#### 3. **Integration Tests - Authentication Flow**
- `test_auth_integration.py` - Complete auth flow
- Register → Login → Access Protected Route
- Duplicate email registration
- Invalid credentials handling
- Logout functionality

#### 4. **End-to-End Tests**
- `test_booking_e2e.py` - Full booking workflow
- Login → View Resource → Book Resource → View Booking
- Booking with conflicts

#### 5. **Security Tests**
- `test_security.py` - Security validation
- SQL injection prevention (parameterized queries)
- XSS prevention (template escaping)
- CSRF protection verification

### Test Requirements Met

✅ **Unit tests for booking logic** (conflict detection, status transitions)  
✅ **Unit tests for Data Access Layer** (CRUD operations independent of Flask routes)  
✅ **Integration test for auth flow** (register → login → access protected route)  
✅ **End-to-end scenario** (booking a resource through the UI)  
✅ **Security checks** (SQL injection, template escaping)  

### Test Configuration

Tests use an in-memory SQLite database (`sqlite:///:memory:`) for isolation and speed. The test configuration is in `pytest.ini`:

- Test paths: `src/tests`
- Test discovery: `test_*.py` files
- Verbose output with short tracebacks

### Writing New Tests

When adding new features, include corresponding tests:

1. **DAL Tests**: Test CRUD operations in `src/tests/test_<model>_dal.py`
2. **Logic Tests**: Test business logic in `src/tests/test_<feature>_logic.py`
3. **Integration Tests**: Test workflows in `src/tests/test_<feature>_integration.py`
4. **Security Tests**: Add security checks to `src/tests/test_security.py`

Use the fixtures in `conftest.py` for common test setup (app, client, sample users, etc.).

## Development Guidelines

1. **Controllers** should only call DAL methods, never issue raw SQL
2. **Models** should only define structure, no business logic
3. **DAL** should handle all database interactions
4. **Views** should only render templates, no logic

This separation ensures maintainability, testability, and clear separation of concerns.

## Contributing

All major changes should be made through GitHub with proper branching and pull requests.

## License

[License information to be added]

---

**Note:** This structure supports AI-driven reasoning and safe automation. All major changes should be made through GitHub with proper branching and pull requests.
