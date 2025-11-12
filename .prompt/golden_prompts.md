# Golden Prompts - High-Impact Prompts and Responses

This file contains high-impact prompts and their successful responses that have proven effective for this project.

## Purpose
Maintain a collection of prompts that generate particularly useful, accurate, or contextually relevant code and solutions for the Campus Resource Hub project.

---

## Golden Prompts

### Content Moderation System - 2024
**Prompt:**
```
I want to make it where both students and staff can flag reviews or report messages. 
The admin should be able to view these. Admin can hide reviews, suspend a user, or 
delete content; actions logged in admin_logs
```

**Context:**
This prompt was effective because it clearly specified:
1. Who can perform actions (students and staff)
2. What actions they can perform (flag/report)
3. What admin should see (flagged/reported content)
4. What admin actions are needed (hide, suspend, delete)
5. Requirement for logging (admin_logs)

**Response Summary:**
- Created complete flagging/reporting system with database models
- Implemented admin moderation interface with separate views for flagged reviews and reported messages
- Added all requested moderation actions (hide, suspend, delete) with proper logging
- Implemented ignore functionality to dismiss false flags/reports
- All actions properly logged in admin_logs table

---

### Student Resource Approval - 2024
**Prompt:**
```
Right now, when a student creates a resource, does the admin need to approve it for 
it to be on the site? If not, we need that function
```

**Context:**
This prompt was effective because it:
1. Asked a clarifying question first (checking current state)
2. Clearly stated the requirement if not already implemented
3. Focused on a specific user role (students) and workflow (approval)

**Response Summary:**
- Implemented role-based resource status assignment
- Students' resources automatically set to 'draft' requiring approval
- Staff/admins can publish immediately
- Updated UI to show appropriate status fields based on user role
- Added clear messaging about approval requirements

---

### Testing Use Cases - 2024
**Prompt:**
```
DONT CHANGE ANYTHING IN THE CODE OR DATABASE. JUST LET ME KNOW IF THESE ARE 
POSSIBLE WITH WHAT WE HAVE: [Use Case 1, 2, 3...]
```

**Context:**
This prompt pattern was highly effective because:
1. Explicitly prevented code changes (user was testing)
2. Requested analysis of existing functionality
3. Provided specific use cases to verify
4. Allowed user to validate system capabilities before requesting changes

**Response Summary:**
- Comprehensive codebase analysis without making changes
- Verified all three use cases were fully supported
- Provided detailed breakdown of how each use case requirement was met
- Confirmed acceptance criteria were all achievable

---

### Bug Fix with Context - 2024
**Prompt:**
```
OperationalError: (sqlite3.OperationalError) no such column: reviews.is_hidden
[Full traceback provided]
```

**Context:**
This prompt was effective because:
1. Provided complete error traceback
2. Showed exact error message and location
3. Enabled quick diagnosis and targeted fix
4. Included database schema context

**Response Summary:**
- Created migration script to add missing column
- Updated DAL to handle missing columns gracefully
- Fixed template errors related to schema changes
- Provided defensive coding to prevent future issues

---

