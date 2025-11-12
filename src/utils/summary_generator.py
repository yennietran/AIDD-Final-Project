"""
Auto-Summary Reporter
Generates natural language summaries of system statistics using LLM
Uses DAL methods directly (not MCP tools) to avoid write operation restrictions

Context Grounding: This feature was developed with reference to project context
materials in /docs/context/ to ensure alignment with project goals and user needs.
Specifically, wireframes in /docs/context/DT/ informed the admin dashboard design,
and process models in /docs/context/APA/ helped shape the reporting workflow.

AI Contribution: This entire module was AI-generated based on requirements for an
AI-powered summary feature. The LLM integration (Ollama, LM Studio, OpenAI) and
statistics aggregation logic were AI-suggested and implemented with team review.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def gather_statistics() -> Dict[str, Any]:
    """
    Gather system statistics using DAL methods (not MCP tools to avoid write operation errors)
    
    Returns:
        Dictionary with aggregated statistics
    """
    from src.data_access.admin_dal import AdminDAL
    from src.data_access.resource_dal import ResourceDAL
    from src.data_access.booking_dal import BookingDAL
    from src.data_access.review_dal import ReviewDAL
    from src.models.models import db, Resource, Booking, Review
    from sqlalchemy import func, case
    
    # Get basic statistics
    basic_stats = AdminDAL.get_statistics()
    
    # Get top 5 most popular resources (by booking count)
    popular_resources_query = db.session.query(
        Resource,
        func.count(Booking.booking_id).label('booking_count'),
        func.avg(Review.rating).label('average_rating')
    ).outerjoin(Booking, Resource.resource_id == Booking.resource_id)\
     .outerjoin(Review, Resource.resource_id == Review.resource_id)\
     .filter(Resource.status == 'published')\
     .group_by(Resource.resource_id)\
     .order_by(func.count(Booking.booking_id).desc(), func.avg(Review.rating).desc())\
     .limit(5).all()
    
    popular_resources = []
    for resource, booking_count, avg_rating in popular_resources_query:
        popular_resources.append({
            'resource_id': resource.resource_id,
            'title': resource.title,
            'category': resource.category,
            'location': resource.location,
            'booking_count': booking_count or 0,
            'average_rating': round(float(avg_rating), 2) if avg_rating else None
        })
    
    # Get recent bookings (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_bookings = BookingDAL.get_all(limit=1000)
    recent_bookings = [b for b in recent_bookings if b.start_datetime >= week_ago]
    
    # Get booking statistics by status
    all_bookings = BookingDAL.get_all(limit=1000)
    booking_status_counts = {}
    for booking in all_bookings:
        status = booking.status or 'unknown'
        booking_status_counts[status] = booking_status_counts.get(status, 0) + 1
    
    # Get resources by category
    all_resources = ResourceDAL.get_all(status='published', limit=100)
    category_counts = {}
    for resource in all_resources:
        category = resource.category or 'Uncategorized'
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Get top rated resources
    top_rated_query = db.session.query(
        Resource,
        func.avg(Review.rating).label('average_rating'),
        func.count(Review.review_id).label('total_reviews')
    ).join(Review, Resource.resource_id == Review.resource_id)\
     .filter(Resource.status == 'published')\
     .group_by(Resource.resource_id)\
     .having(func.count(Review.review_id) > 0)\
     .order_by(func.avg(Review.rating).desc())\
     .limit(5).all()
    
    top_rated = []
    for resource, avg_rating, total_reviews in top_rated_query:
        top_rated.append({
            'resource_id': resource.resource_id,
            'title': resource.title,
            'average_rating': round(float(avg_rating), 2),
            'total_reviews': total_reviews
        })
    
    # Calculate booking trends (this week vs last week)
    two_weeks_ago = datetime.now() - timedelta(days=14)
    last_week_bookings = [b for b in all_bookings if two_weeks_ago <= b.start_datetime < week_ago]
    this_week_count = len(recent_bookings)
    last_week_count = len(last_week_bookings)
    
    trend = "increased" if this_week_count > last_week_count else "decreased" if this_week_count < last_week_count else "stable"
    trend_percentage = abs((this_week_count - last_week_count) / last_week_count * 100) if last_week_count > 0 else 0
    
    return {
        'basic_stats': basic_stats,
        'popular_resources': popular_resources,
        'top_rated_resources': top_rated,
        'recent_bookings_count': this_week_count,
        'last_week_bookings_count': last_week_count,
        'booking_trend': trend,
        'trend_percentage': round(trend_percentage, 1),
        'booking_status_counts': booking_status_counts,
        'category_counts': category_counts,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def format_statistics_for_llm(stats: Dict[str, Any]) -> str:
    """
    Format statistics into a prompt-friendly format for LLM
    
    Args:
        stats: Statistics dictionary from gather_statistics()
        
    Returns:
        Formatted string with statistics
    """
    prompt = f"""Generate a weekly summary report for the Campus Resource Hub system based on the following statistics:

SYSTEM OVERVIEW:
- Total Users: {stats['basic_stats']['total_users']}
- Total Resources: {stats['basic_stats']['total_resources']}
- Total Bookings: {stats['basic_stats']['total_bookings']}
- Pending Bookings: {stats['basic_stats']['pending_bookings']}
- Total Reviews: {stats['basic_stats']['total_reviews']}
- Average Rating: {stats['basic_stats']['average_rating']}/5.0

BOOKING TRENDS:
- Bookings this week: {stats['recent_bookings_count']}
- Bookings last week: {stats['last_week_bookings_count']}
- Trend: {stats['booking_trend'].upper()} ({stats['trend_percentage']}% change)

BOOKING STATUS BREAKDOWN:
"""
    for status, count in stats['booking_status_counts'].items():
        prompt += f"- {status.title()}: {count}\n"
    
    prompt += f"\nTOP 5 MOST POPULAR RESOURCES (by booking count):\n"
    for i, resource in enumerate(stats['popular_resources'][:5], 1):
        booking_count = resource.get('booking_count', 0)
        avg_rating = resource.get('average_rating', 0)
        prompt += f"{i}. {resource.get('title', 'Unknown')} - {booking_count} bookings"
        if avg_rating:
            prompt += f", {round(avg_rating, 2)}/5.0 rating"
        prompt += "\n"
    
    if stats['top_rated_resources']:
        prompt += f"\nTOP 5 HIGHEST RATED RESOURCES:\n"
        for i, resource in enumerate(stats['top_rated_resources'][:5], 1):
            prompt += f"{i}. {resource['title']} - {resource['average_rating']}/5.0 ({resource['total_reviews']} reviews)\n"
    
    prompt += f"\nRESOURCES BY CATEGORY:\n"
    for category, count in sorted(stats['category_counts'].items(), key=lambda x: x[1], reverse=True):
        prompt += f"- {category}: {count} resources\n"
    
    prompt += f"\nGenerate a natural, engaging weekly summary report (2-3 paragraphs) highlighting key insights, trends, and notable statistics. Be concise but informative. Focus on what administrators should know about system usage and performance."
    
    return prompt


def generate_summary_with_llm(stats: Dict[str, Any], llm_provider: str = 'ollama', model: str = 'llama3.2') -> str:
    """
    Generate summary using LLM
    
    Args:
        stats: Statistics dictionary
        llm_provider: 'ollama', 'lm_studio', or 'openai'
        model: Model name to use
        
    Returns:
        Generated summary text
    """
    prompt = format_statistics_for_llm(stats)
    
    try:
        if llm_provider == 'ollama':
            return _generate_with_ollama(prompt, model)
        elif llm_provider == 'lm_studio':
            return _generate_with_lm_studio(prompt, model)
        elif llm_provider == 'openai':
            return _generate_with_openai(prompt, model)
        else:
            # Fallback: return formatted statistics without LLM
            return _generate_fallback_summary(stats)
    except Exception as e:
        # If LLM fails, return fallback summary
        print(f"LLM generation failed: {e}")
        return _generate_fallback_summary(stats)


def _generate_with_ollama(prompt: str, model: str = 'llama3.2') -> str:
    """Generate summary using Ollama"""
    try:
        import requests
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'Summary generation failed.')
        else:
            raise Exception(f"Ollama API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to Ollama. Make sure Ollama is running on localhost:11434")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")


def _generate_with_lm_studio(prompt: str, model: str = 'local-model') -> str:
    """Generate summary using LM Studio"""
    try:
        import requests
        
        response = requests.post(
            'http://localhost:1234/v1/chat/completions',
            json={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that generates concise, informative reports.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"LM Studio API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to LM Studio. Make sure LM Studio is running on localhost:1234")
    except Exception as e:
        raise Exception(f"LM Studio error: {str(e)}")


def _generate_with_openai(prompt: str, model: str = 'gpt-3.5-turbo') -> str:
    """Generate summary using OpenAI API"""
    try:
        import os
        import requests
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY environment variable not set")
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that generates concise, informative reports.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API returned status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"OpenAI error: {str(e)}")


def _generate_fallback_summary(stats: Dict[str, Any]) -> str:
    """Generate a summary without LLM (fallback)"""
    summary = f"""# Weekly System Summary
Generated: {stats['generated_at']}

## System Overview
The Campus Resource Hub currently has {stats['basic_stats']['total_users']} registered users, {stats['basic_stats']['total_resources']} published resources, and {stats['basic_stats']['total_bookings']} total bookings. The system has received {stats['basic_stats']['total_reviews']} reviews with an average rating of {stats['basic_stats']['average_rating']}/5.0.

## Booking Activity
This week saw {stats['recent_bookings_count']} new bookings, compared to {stats['last_week_bookings_count']} last week. This represents a {stats['booking_trend'].upper()} trend ({stats['trend_percentage']}% change). There are currently {stats['basic_stats']['pending_bookings']} pending booking requests awaiting approval.

## Top Resources
"""
    
    if stats['popular_resources']:
        summary += "The most popular resources this week:\n"
        for i, resource in enumerate(stats['popular_resources'][:5], 1):
            booking_count = resource.get('booking_count', 0)
            summary += f"{i}. {resource.get('title', 'Unknown')} - {booking_count} bookings\n"
    
    if stats['top_rated_resources']:
        summary += "\nHighest rated resources:\n"
        for i, resource in enumerate(stats['top_rated_resources'][:5], 1):
            summary += f"{i}. {resource['title']} - {resource['average_rating']}/5.0 ({resource['total_reviews']} reviews)\n"
    
    summary += "\n## Resource Distribution\n"
    for category, count in sorted(stats['category_counts'].items(), key=lambda x: x[1], reverse=True):
        summary += f"- {category}: {count} resources\n"
    
    return summary

