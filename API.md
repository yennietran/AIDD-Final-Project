# Campus Resource Hub - API Documentation

This document describes the RESTful API endpoints for the Campus Resource Hub application.

## Base URL

All API endpoints are prefixed with `/api`:

```
http://localhost:5000/api
```

## Quick Reference

All suggested endpoints are implemented:

- ✅ `POST /api/auth/register` — create user
- ✅ `POST /api/auth/login` — obtain session
- ✅ `GET /api/resources` — list/search resources
- ✅ `GET /api/resources/<id>` — resource detail
- ✅ `POST /api/resources` — create a resource (auth required)
- ✅ `PUT /api/resources/<id>` — update
- ✅ `DELETE /api/resources/<id>` — delete
- ✅ `POST /api/bookings` — request booking
- ✅ `GET /api/bookings/<id>` — booking detail
- ✅ `PUT /api/bookings/<id>/approve` — approve booking (staff/admin or owner)
- ✅ `POST /api/messages` — send message
- ✅ `POST /api/reviews` — submit review
- ✅ `GET /api/admin/stats` — usage metrics (admin)

## Authentication

Most endpoints require authentication via Flask-Login session management. For API-only access, you would typically use JWT tokens (not implemented in this version).

## Response Format

All API responses follow this structure:

**Success Response:**
```json
{
    "success": true,
    "message": "Optional success message",
    "data": { ... }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Error message description"
}
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Authentication Endpoints

### POST /api/auth/register

Create a new user account.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "student",
    "department": "Computer Science"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "User created successfully",
    "user": {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "student",
        "department": "Computer Science"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "Email already exists"
}
```

---

### POST /api/auth/login

Login and obtain session.

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "password123"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "student",
        "department": "Computer Science"
    }
}
```

**Error Response (401 Unauthorized):**
```json
{
    "success": false,
    "error": "Invalid email or password"
}
```

---

## Resource Endpoints

### GET /api/resources

List or search resources.

**Query Parameters:**
- `q` (optional) - Search query (searches title, description, location)
- `category` (optional) - Filter by category
- `status` (optional) - Filter by status (default: `published`)
- `owner_id` (optional) - Filter by owner ID
- `limit` (optional) - Maximum results (default: 50)

**Example Request:**
```
GET /api/resources?q=study&category=Study Rooms&limit=10
```

**Response (200 OK):**
```json
{
    "success": true,
    "count": 10,
    "resources": [
        {
            "resource_id": 1,
            "title": "Study Room 201",
            "description": "Quiet study space with whiteboard",
            "category": "Study Rooms",
            "location": "Library 2F",
            "capacity": 4,
            "images": ["https://example.com/image1.jpg"],
            "availability_rules": {
                "monday": "9:00-17:00",
                "tuesday": "9:00-17:00"
            },
            "status": "published",
            "owner_id": 1,
            "created_at": "2024-01-01T00:00:00"
        }
    ]
}
```

---

### GET /api/resources/<id>

Get resource detail by ID.

**Response (200 OK):**
```json
{
    "success": true,
    "resource": {
        "resource_id": 1,
        "title": "Study Room 201",
        "description": "Quiet study space with whiteboard",
        "category": "Study Rooms",
        "location": "Library 2F",
        "capacity": 4,
        "images": ["https://example.com/image1.jpg"],
        "availability_rules": {
            "monday": "9:00-17:00"
        },
        "status": "published",
        "owner_id": 1,
        "created_at": "2024-01-01T00:00:00"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "error": "Resource not found"
}
```

---

### POST /api/resources

Create a new resource (authentication required).

**Request Body:**
```json
{
    "title": "Study Room 201",
    "description": "Quiet study space with whiteboard",
    "category": "Study Rooms",
    "location": "Library 2F",
    "capacity": 4,
    "images": ["https://example.com/image1.jpg"],
    "availability_rules": {
        "monday": "9:00-17:00",
        "tuesday": "9:00-17:00"
    },
    "status": "draft"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Resource created successfully",
    "resource": {
        "resource_id": 1,
        "title": "Study Room 201",
        ...
    }
}
```

---

### PUT /api/resources/<id>

Update a resource (authentication required, owner or admin only).

**Request Body:** (all fields optional)
```json
{
    "title": "Updated Title",
    "description": "Updated description",
    "status": "published"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Resource updated successfully",
    "resource": { ... }
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": "You do not have permission to update this resource"
}
```

---

### DELETE /api/resources/<id>

Delete a resource (authentication required, owner or admin only).

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Resource deleted successfully"
}
```

---

## Booking Endpoints

### POST /api/bookings

Request a booking (authentication required).

**Request Body:**
```json
{
    "resource_id": 1,
    "start_datetime": "2024-12-15T10:00:00",
    "end_datetime": "2024-12-15T12:00:00"
}
```

**Note:** Datetime format should be ISO 8601 (e.g., `2024-12-15T10:00:00` or `2024-12-15T10:00:00Z`)

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Booking request created",
    "booking": {
        "booking_id": 1,
        "resource_id": 1,
        "requester_id": 2,
        "start_datetime": "2024-12-15T10:00:00",
        "end_datetime": "2024-12-15T12:00:00",
        "status": "pending",
        "created_at": "2024-12-01T00:00:00"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "Time conflict detected. Resource is already booked for this time"
}
```

**Note:** Booking status is automatically set to `approved` for staff/admin users or resource owners, otherwise `pending`.

---

### GET /api/bookings/<id>

Get booking detail (authentication required).

**Response (200 OK):**
```json
{
    "success": true,
    "booking": {
        "booking_id": 1,
        "resource_id": 1,
        "requester_id": 2,
        "start_datetime": "2024-12-15T10:00:00",
        "end_datetime": "2024-12-15T12:00:00",
        "status": "pending",
        "created_at": "2024-12-01T00:00:00",
        "updated_at": "2024-12-01T00:00:00"
    }
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": "You do not have permission to view this booking"
}
```

---

### PUT /api/bookings/<id>/approve

Approve a booking (authentication required, staff/admin or resource owner only).

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Booking approved",
    "booking": {
        "booking_id": 1,
        "status": "approved",
        ...
    }
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": "You do not have permission to approve this booking"
}
```

---

## Message Endpoints

### POST /api/messages

Send a message (authentication required).

**Request Body:**
```json
{
    "receiver_id": 2,
    "content": "Hello, I'm interested in your resource. Is it available this weekend?"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Message sent successfully",
    "message_data": {
        "message_id": 1,
        "sender_id": 1,
        "receiver_id": 2,
        "content": "Hello, I'm interested in your resource...",
        "timestamp": "2024-12-01T00:00:00"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "Cannot send message to yourself"
}
```

---

## Review Endpoints

### POST /api/reviews

Submit a review (authentication required).

**Request Body:**
```json
{
    "resource_id": 1,
    "rating": 5,
    "comment": "Great resource! Very clean and well-maintained."
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Review submitted successfully",
    "review": {
        "review_id": 1,
        "resource_id": 1,
        "reviewer_id": 2,
        "rating": 5,
        "comment": "Great resource! Very clean and well-maintained.",
        "timestamp": "2024-12-01T00:00:00"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "You can only review resources you have booked and completed"
}
```

**Note:** Users can only review resources they have booked and completed. Rating must be between 1 and 5.

---

## Admin Endpoints

### GET /api/admin/stats

Get usage metrics (authentication required, admin only).

**Response (200 OK):**
```json
{
    "success": true,
    "stats": {
        "total_users": 150,
        "total_resources": 45,
        "total_bookings": 320,
        "pending_bookings": 12,
        "total_reviews": 89,
        "average_rating": 4.2
    }
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": "Admin access required"
}
```

---

## Example Usage

### Using cURL

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "student"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }' \
  -c cookies.txt
```

**List resources:**
```bash
curl http://localhost:5000/api/resources?q=study&category=Study Rooms
```

**Create a resource (requires authentication):**
```bash
curl -X POST http://localhost:5000/api/resources \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Study Room 201",
    "description": "Quiet study space",
    "category": "Study Rooms",
    "location": "Library 2F",
    "capacity": 4,
    "status": "published"
  }'
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api"

# Register
response = requests.post(f"{base_url}/auth/register", json={
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "student"
})
print(response.json())

# Login
session = requests.Session()
response = session.post(f"{base_url}/auth/login", json={
    "email": "john@example.com",
    "password": "password123"
})
print(response.json())

# List resources
response = session.get(f"{base_url}/resources", params={
    "q": "study",
    "category": "Study Rooms"
})
print(response.json())

# Create booking
response = session.post(f"{base_url}/bookings", json={
    "resource_id": 1,
    "start_datetime": "2024-12-15T10:00:00",
    "end_datetime": "2024-12-15T12:00:00"
})
print(response.json())
```

---

## Notes

1. **Authentication:** Currently uses Flask-Login session management. For production API use, consider implementing JWT tokens.

2. **Datetime Format:** All datetime fields use ISO 8601 format (e.g., `2024-12-15T10:00:00`).

3. **JSON Fields:** The `images` and `availability_rules` fields are stored as JSON strings in the database but are automatically parsed in API responses.

4. **Permissions:**
   - Resource owners can edit/delete their own resources
   - Admins have full access
   - Staff/Admin users can approve bookings
   - Users can only review resources they've booked and completed

5. **Error Handling:** All endpoints return appropriate HTTP status codes and error messages in JSON format.

