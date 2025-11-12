"""
Model Context Protocol (MCP) Server
Main server implementation for AI agent database access

This server provides a structured interface for AI tools to safely query
the Campus Resource Hub database in read-only mode.
"""
from mcp_tools import (
    query_resources,
    get_resource_summary,
    query_bookings,
    check_availability,
    query_reviews,
    get_resource_ratings,
    get_popular_resources,
    query_users,
    MCPDatabaseError
)
import json
from typing import Dict, Any, Optional


class MCPServer:
    """
    MCP Server for safe, read-only database access
    """
    
    def __init__(self):
        """Initialize the MCP server"""
        self.tools = {
            'query_resources': self._query_resources,
            'get_resource_summary': self._get_resource_summary,
            'query_bookings': self._query_bookings,
            'check_availability': self._check_availability,
            'query_reviews': self._query_reviews,
            'get_resource_ratings': self._get_resource_ratings,
            'get_popular_resources': self._get_popular_resources,
            'query_users': self._query_users,
        }
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool with given parameters
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters as dictionary
            
        Returns:
            Dictionary with tool results or error information
        """
        if tool_name not in self.tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            result = self.tools[tool_name](**parameters)
            return {
                "success": True,
                "data": result
            }
        except MCPDatabaseError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _query_resources(self, **kwargs) -> Any:
        """Query resources tool"""
        return query_resources(
            category=kwargs.get('category'),
            location=kwargs.get('location'),
            status=kwargs.get('status'),
            limit=kwargs.get('limit', 50)
        )
    
    def _get_resource_summary(self, **kwargs) -> Any:
        """Get resource summary tool"""
        resource_id = kwargs.get('resource_id')
        if not resource_id:
            raise ValueError("resource_id is required")
        return get_resource_summary(resource_id)
    
    def _query_bookings(self, **kwargs) -> Any:
        """Query bookings tool"""
        return query_bookings(
            resource_id=kwargs.get('resource_id'),
            requester_id=kwargs.get('requester_id'),
            status=kwargs.get('status'),
            start_date=kwargs.get('start_date'),
            end_date=kwargs.get('end_date'),
            limit=kwargs.get('limit', 50)
        )
    
    def _check_availability(self, **kwargs) -> Any:
        """Check availability tool"""
        resource_id = kwargs.get('resource_id')
        start_datetime = kwargs.get('start_datetime')
        end_datetime = kwargs.get('end_datetime')
        
        if not all([resource_id, start_datetime, end_datetime]):
            raise ValueError("resource_id, start_datetime, and end_datetime are required")
        
        return check_availability(resource_id, start_datetime, end_datetime)
    
    def _query_reviews(self, **kwargs) -> Any:
        """Query reviews tool"""
        return query_reviews(
            resource_id=kwargs.get('resource_id'),
            reviewer_id=kwargs.get('reviewer_id'),
            min_rating=kwargs.get('min_rating'),
            limit=kwargs.get('limit', 50)
        )
    
    def _get_resource_ratings(self, **kwargs) -> Any:
        """Get resource ratings tool"""
        resource_id = kwargs.get('resource_id')
        if not resource_id:
            raise ValueError("resource_id is required")
        return get_resource_ratings(resource_id)
    
    def _get_popular_resources(self, **kwargs) -> Any:
        """Get popular resources tool"""
        return get_popular_resources(limit=kwargs.get('limit', 10))
    
    def _query_users(self, **kwargs) -> Any:
        """Query users tool (limited fields for privacy)"""
        return query_users(
            role=kwargs.get('role'),
            department=kwargs.get('department'),
            limit=kwargs.get('limit', 50)
        )
    
    def list_tools(self) -> Dict[str, Any]:
        """
        List all available MCP tools
        
        Returns:
            Dictionary with tool names and descriptions
        """
        return {
            "tools": [
                {
                    "name": "query_resources",
                    "description": "Search resources by category, location, or status",
                    "parameters": ["category", "location", "status", "limit"]
                },
                {
                    "name": "get_resource_summary",
                    "description": "Get detailed resource information with booking and review stats",
                    "parameters": ["resource_id"]
                },
                {
                    "name": "query_bookings",
                    "description": "Search bookings by various filters",
                    "parameters": ["resource_id", "requester_id", "status", "start_date", "end_date", "limit"]
                },
                {
                    "name": "check_availability",
                    "description": "Check if a resource is available for a time period",
                    "parameters": ["resource_id", "start_datetime", "end_datetime"]
                },
                {
                    "name": "query_reviews",
                    "description": "Query reviews with optional filters",
                    "parameters": ["resource_id", "reviewer_id", "min_rating", "limit"]
                },
                {
                    "name": "get_resource_ratings",
                    "description": "Get rating statistics for a resource",
                    "parameters": ["resource_id"]
                },
                {
                    "name": "get_popular_resources",
                    "description": "Get most popular resources by booking count",
                    "parameters": ["limit"]
                },
                {
                    "name": "query_users",
                    "description": "Query users (limited fields for privacy)",
                    "parameters": ["role", "department", "limit"]
                }
            ]
        }


# Global MCP server instance
mcp_server = MCPServer()


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance"""
    return mcp_server

