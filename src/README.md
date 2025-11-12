# Campus Resource Hub - Source Code

This directory contains the main application source code following the MVC (Model-View-Controller) architecture pattern.

## Directory Structure

```
src/
├── controllers/      # Flask routes and blueprints (Controller Layer)
├── models/          # ORM classes and database models (Model Layer)
├── views/           # HTML/Jinja templates (View Layer)
├── data_access/     # Encapsulated CRUD operations (Data Access Layer)
├── static/          # Static files (CSS, JS, images)
└── tests/           # Unit tests for business logic
```

## Architecture

### Model Layer (`models/`)
- Contains SQLAlchemy ORM models
- Defines database schema and relationships
- No business logic, only data structure

### View Layer (`views/`)
- Jinja2 HTML templates
- Base template with navigation and layout
- Page-specific templates extending base

### Controller Layer (`controllers/`)
- Flask routes and blueprints
- Handles HTTP requests and responses
- Coordinates between views and data access layer
- No direct database queries

### Data Access Layer (`data_access/`)
- Encapsulates all database operations
- CRUD methods for each model
- Controllers use DAL methods, never raw SQL
- Business logic for data operations

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/init_db.py

# Run the application
python app.py
```

### Running Tests

```bash
pytest
```

## Development Guidelines

1. **Controllers** should only call DAL methods, never issue raw SQL
2. **Models** should only define structure, no business logic
3. **DAL** should handle all database interactions
4. **Views** should only render templates, no logic

This separation ensures maintainability, testability, and clear separation of concerns.

