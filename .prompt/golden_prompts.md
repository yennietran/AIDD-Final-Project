# Golden Prompts - High-Impact Prompts and Responses

This file contains high-impact prompts and their successful responses that have proven effective for this project.

## Purpose
Maintain a collection of prompts that generate particularly useful, accurate, or contextually relevant code and solutions for the Campus Resource Hub project.

---

## Golden Prompts

### Resource Filtering and Automated Messaging - November 2024
**Prompt:**
```
when you click on the resources page, i also want to be able to filter by date, time, sort by, min capaciity. 
for filtering by status, make sure only the admin can have this option. for the required things when creating resource, add a * next to them to indicate it's required
notify creator their resource is successfully published by sending them a message in addition to the notification on the screen we have at the moment. so for example, when a staff pubishhes a resource, then it sends them a message saying it was successful. and for when an admin approves a resource made by a student, send the student a message of confirmation too
```

**Context:**
This prompt was effective because it:
1. Clearly specified multiple related features in one request (filtering, UI improvements, messaging)
2. Explicitly stated access control requirements (admin-only status filter)
3. Provided specific examples of when messages should be sent
4. Combined UI improvements with backend functionality

**Response Summary:**
- Added comprehensive filtering to resources page (date, time, min capacity, sort by)
- Implemented date/time availability checking using existing BookingDAL methods
- Made status filter admin-only with role check
- Updated all required fields to use red asterisks for better UX
- Implemented automated messaging for:
  - Staff/admin resource publishing (self-confirmation message)
  - Admin approval of student resources (admin-to-student message)
- Messages include resource details and confirmation text
- Error handling ensures resource operations don't fail if messaging fails

**Key Learning:**
Grouping related features in one prompt allows AI to understand the full context and implement a cohesive solution. The explicit examples helped clarify the messaging requirements.

---

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

### Auto-Summary Reporter Implementation - 2024
**Prompt:**
```
OK CAN YOU IMPLEMENT THE AUTO SUMMARRY REPORTER?
```

**Context:**
This prompt was effective because:
1. User had already asked which AI feature was easiest to implement
2. Clear, direct request for implementation
3. Built on previous analysis of available options
4. User was ready to proceed with implementation

**Response Summary:**
- Implemented complete Auto-Summary Reporter feature
- Created statistics aggregation using DAL methods
- Integrated multiple LLM providers (Ollama, LM Studio, OpenAI)
- Added fallback mode for when LLM is unavailable
- Created admin interface with LLM configuration options
- Fixed initial MCP tool restriction issues by switching to DAL methods
- Generated comprehensive documentation

**Why This Was Golden:**
- Single prompt led to complete feature implementation
- AI correctly identified and fixed technical issues (MCP restrictions)
- Generated both code and documentation
- Included error handling and fallback mechanisms
- Created user-friendly admin interface

---

### Reflection and Ethics Documentation - 2024
**Prompt:**
```
ok add that
[Referring to adding attribution comments and ethical implications discussion]
```

**Context:**
This prompt was effective because:
1. User had identified missing requirements
2. Clear directive to add specific documentation
3. Built on previous conversation about requirements
4. User wanted comprehensive documentation updates

**Response Summary:**
- Created comprehensive AI_REFLECTION.md addressing all 4 reflection questions
- Added ethical implications discussion covering transparency, academic integrity, bias
- Added attribution comments throughout codebase
- Updated README with AI collaboration insights and ethical considerations
- Added AI tools disclosure to dev_notes.md

**Why This Was Golden:**
- Single prompt led to complete documentation suite
- Addressed all academic integrity requirements
- Created reflection document that comprehensively covers all questions
- Maintained consistency across all documentation files
- Ensured full compliance with project requirements

---

