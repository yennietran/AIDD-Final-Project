# Model Context Protocol (MCP) Integration

This directory contains the Model Context Protocol (MCP) implementation for the Campus Resource Hub project. MCP enables safe, read-only interaction between AI agents and the SQLite database.

## Overview

MCP provides a structured interface for AI tools to query and inspect database content without the ability to modify data. This enables features such as:

- **Intelligent Search**: AI-powered resource discovery
- **Summaries**: Automated resource and booking summaries
- **Analytics**: Data insights and reporting
- **Recommendations**: Context-aware resource suggestions

## Architecture

```
mcp/
├── mcp_server.py      # Main MCP server implementation
├── mcp_tools.py       # Read-only database query tools
└── README.md          # This file
```

## Security

**All MCP operations are READ-ONLY**. The implementation:

- Uses parameterized queries to prevent SQL injection
- Validates all queries before execution
- Returns structured JSON responses
- Logs all queries for audit purposes
- Never allows INSERT, UPDATE, DELETE, or DROP operations

## Available Tools

### Resource Queries

- `query_resources` - Search resources by category, location, status
- `get_resource_summary` - Get detailed resource information
- `get_popular_resources` - Find most booked resources

### Booking Queries

- `query_bookings` - Search bookings by date range, status, resource
- `get_booking_summary` - Get booking statistics and patterns
- `check_availability` - Check resource availability for date ranges

### Review Queries

- `query_reviews` - Get reviews for resources
- `get_resource_ratings` - Calculate average ratings and review counts

### User Queries

- `query_users` - Search users by role, department (limited fields)
- `get_user_stats` - Get user activity statistics

## Usage Example

```python
from mcp.mcp_tools import query_resources, get_resource_summary

# Search for study rooms
resources = query_resources(category="study room", status="published")

# Get detailed summary
summary = get_resource_summary(resource_id=1)
```

## Integration with AI Agents

MCP tools are designed to be called by AI agents (such as Cursor, Copilot, or custom AI assistants) to:

1. Understand current database state
2. Generate intelligent responses based on data
3. Provide context-aware recommendations
4. Create summaries and reports

## Logging

All MCP queries are logged in `.prompt/dev_notes.md` for:
- Audit trail
- Performance monitoring
- Usage analytics
- Debugging

## Future Enhancements

- Natural language query interface
- Advanced analytics and insights
- Predictive booking patterns
- Resource recommendation engine

---

**Note**: MCP is a recommended feature for this project. Implementation should follow the MCP specification and maintain strict read-only access to the database.

