# AI Summary Reporter

## Overview

The Auto-Summary Reporter is an AI-powered feature that generates natural language summaries of system statistics and trends for the Campus Resource Hub. It uses existing MCP tools to gather data from the database and leverages LLMs to create engaging, informative reports.

## Features

- **Automatic Data Aggregation**: Uses MCP tools to gather statistics from the database
- **LLM-Powered Summaries**: Generates natural language reports using local or cloud LLMs
- **Multiple LLM Support**: Works with Ollama, LM Studio, or OpenAI API
- **Fallback Mode**: Generates summaries without LLM if unavailable
- **Comprehensive Statistics**: Includes booking trends, popular resources, ratings, and more

## Access

Navigate to: **Admin Dashboard → AI Summary Report**

Or directly: `/admin/summary`

## LLM Configuration

### Option 1: Ollama (Recommended for Local)

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama3.2`
3. Ensure Ollama is running on `localhost:11434`
4. Access the summary page - it will automatically use Ollama

**Default Settings:**
- Provider: `ollama`
- Model: `llama3.2`

### Option 2: LM Studio

1. Install [LM Studio](https://lmstudio.ai/)
2. Load a model in LM Studio
3. Start the local server (usually runs on `localhost:1234`)
4. Select "LM Studio" as provider on the summary page

**Settings:**
- Provider: `lm_studio`
- Model: Name of your loaded model

### Option 3: OpenAI API

1. Set environment variable: `export OPENAI_API_KEY=your-api-key`
2. Select "OpenAI API" as provider on the summary page

**Settings:**
- Provider: `openai`
- Model: `gpt-3.5-turbo` or `gpt-4`

### Option 4: Fallback (No LLM)

If no LLM is available, the system will automatically generate a structured summary using the gathered statistics. Select "No (Fallback)" in the "Use LLM" dropdown.

## What's Included in the Summary

The summary includes:

1. **System Overview**
   - Total users, resources, bookings, reviews
   - Average rating across all resources

2. **Booking Trends**
   - Bookings this week vs. last week
   - Trend analysis (increased/decreased/stable)
   - Booking status breakdown

3. **Top Resources**
   - Top 5 most popular resources (by booking count)
   - Top 5 highest rated resources (by average rating)

4. **Resource Distribution**
   - Resources grouped by category

## Technical Details

### Data Sources

The summary uses MCP tools to safely query the database:
- `get_popular_resources()` - Most booked resources
- `query_bookings()` - Booking statistics and trends
- `query_resources()` - Resource distribution
- `get_resource_ratings()` - Review and rating data
- `AdminDAL.get_statistics()` - System-wide statistics

### Implementation

- **Module**: `src/utils/summary_generator.py`
- **Route**: `src/controllers/admin.py` → `summary()`
- **Template**: `src/views/admin/summary.html`

### Security

- All database queries use read-only MCP tools
- No write operations are performed
- Admin-only access (requires admin role)
- All queries are parameterized to prevent SQL injection

## Customization

You can customize the summary by:

1. **Modifying the prompt** in `format_statistics_for_llm()` function
2. **Adding new statistics** in `gather_statistics()` function
3. **Adjusting LLM parameters** (temperature, max_tokens) in the generation functions

## Troubleshooting

### "Could not connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check if it's accessible at `http://localhost:11434`
- Verify the model is pulled: `ollama list`

### "Could not connect to LM Studio"
- Ensure LM Studio local server is running
- Check if it's accessible at `http://localhost:1234`
- Verify a model is loaded in LM Studio

### "OPENAI_API_KEY environment variable not set"
- Set the environment variable before running Flask
- Or use Ollama/LM Studio for local development

### Summary shows fallback mode
- This is normal if no LLM is available
- The fallback summary still provides all statistics
- To use LLM, ensure one of the LLM services is running

## Example Output

The AI-generated summary will look like:

```
This week, the Campus Resource Hub saw 45 new bookings, representing a 12% 
increase from last week's 40 bookings. The system currently has 150 registered 
users managing 25 published resources.

The most popular resource this week was "Study Room 201" with 15 bookings, 
followed by "Conference Room A" with 12 bookings. The highest-rated resource 
is "Lab Equipment Set" with a 4.8/5.0 average rating from 23 reviews.

Booking activity shows healthy growth, with 38 approved bookings and 7 pending 
approvals. The system maintains a strong average rating of 4.2/5.0 across all 
resources, indicating high user satisfaction.
```

## Future Enhancements

Potential improvements:
- Scheduled automatic summaries (daily/weekly)
- Email delivery of summaries
- Customizable time ranges
- Export to PDF/CSV
- Historical trend comparisons
- Resource-specific summaries

