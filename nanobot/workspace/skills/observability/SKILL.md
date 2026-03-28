---
name: observability
description: Use observability tools to investigate system health and errors
always: true
---

# Observability Skill

You have access to observability tools for querying logs and traces.

## Available Tools

### Logs (VictoriaLogs)
- `mcp_obs_logs_search` — Search logs using LogsQL queries
- `mcp_obs_logs_error_count` — Count errors over a time window

### Traces (VictoriaTraces)
- `mcp_obs_traces_list` — List recent traces for a service
- `mcp_obs_traces_get` — Fetch a specific trace by ID

### Cron
- `cron` — Schedule recurring tasks

## Strategy

### When the user asks "What went wrong?" or "Check system health":

1. **Start with `mcp_obs_logs_error_count`** to see if there are recent errors
   - Use a narrow time window (e.g., "10m" for last 10 minutes)
   - Filter by service name: "Learning Management Service"

2. **If errors exist, use `mcp_obs_logs_search`** to inspect them
   - Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
   - Look for `trace_id` in the log entries
   - Note the error message and failing operation

3. **If you find a trace_id, use `mcp_obs_traces_get`** to fetch the full trace
   - This shows the complete request flow and where it failed
   - Look for spans with errors

4. **Summarize findings concisely in one coherent response**
   - Do not dump raw JSON
   - Explain what went wrong in plain language
   - Mention: affected service, root failing operation, error type
   - Cite both log evidence AND trace evidence

### Example investigation flow:

```
1. mcp_obs_logs_error_count(time_range="10m", service="Learning Management Service")
   → Found 5 errors

2. mcp_obs_logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR', limit=5)
   → Found trace_id: abc123...
   → Error: "PostgreSQL connection failed"

3. mcp_obs_traces_get(trace_id="abc123...")
   → Trace shows: backend → db_query span failed with SQLAlchemy error

4. Summary: "The LMS backend failed to connect to PostgreSQL. The error occurred in the db_query operation when executing SELECT from items table. SQLAlchemy raised a connection refused error. This affected 5 requests in the last 10 minutes."
```

## Response format

- Keep responses concise and actionable
- Highlight the root cause if found
- Mention affected services and time range
- Always cite both log and trace evidence when available
