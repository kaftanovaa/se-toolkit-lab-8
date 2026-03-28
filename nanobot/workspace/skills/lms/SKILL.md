---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to the LMS (Learning Management System) via MCP tools. Use them to provide real-time data about the course.

## Available Tools

- `lms_health` - Check if the LMS backend is healthy and get the total item count
- `lms_labs` - Get the list of all available labs
- `lms_pass_rates` - Get pass rates for a specific lab (requires `lab` parameter)
- `lms_scores` - Get scores for a specific lab (requires `lab` parameter)
- `lms_learners` - Get list of learners
- `lms_groups` - Get group performance data
- `lms_timeline` - Get submission timeline
- `lms_top_learners` - Get top performing learners
- `lms_completion_rate` - Get completion rate for a lab
- `lms_sync_pipeline` - Trigger ETL sync pipeline

## Strategy

### When user asks about scores, pass rates, completion, groups, timeline, or top learners WITHOUT naming a lab:

1. First call `lms_labs` to get the list of available labs
2. If multiple labs exist, ask the user to choose one
3. Use each lab's `title` field as the user-facing label when presenting choices
4. Once the user selects a lab, call the appropriate tool with the lab identifier

### Example flow for "Show me the scores":

1. Call `lms_labs()` to get available labs
2. If multiple labs: "Which lab would you like to see scores for? Here are the options: [list lab titles]"
3. After user chooses, call `lms_scores(lab="<lab-id>")`
4. Format the results nicely with percentages and counts

### When user asks "what can you do?":

Explain your current capabilities:
- You can query the LMS backend for real-time data
- You can check system health, view labs, see pass rates and scores
- You can show learner performance, group statistics, and submission timelines
- You don't have access to external web search (unless configured separately)

## Formatting

- Format percentages as "XX%" not decimals
- Show counts as whole numbers
- Keep responses concise but informative
- Use bold for key metrics (e.g., **85%** pass rate)

## Important Notes

- Always use live data from MCP tools, not cached or assumed information
- If a tool returns an error, explain what went wrong clearly
- If the backend is unhealthy, suggest running `lms_sync_pipeline` to refresh data
