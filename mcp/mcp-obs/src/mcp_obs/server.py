"""
MCP server for observability tools.

Provides tools to query VictoriaLogs and VictoriaTraces.
"""

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Observability service settings."""
    
    # VictoriaLogs HTTP API endpoint
    victorialogs_url: str = "http://victorialogs:9428"
    
    # VictoriaTraces HTTP API endpoint (Jaeger-compatible)
    victoriatraces_url: str = "http://victoriatraces:10428"


settings = Settings()
server = Server("mcp-obs")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available observability tools."""
    return [
        Tool(
            name="logs_search",
            description="Search logs by keyword and/or time range using LogsQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "LogsQL query (e.g., 'service.name:\"Learning Management Service\" severity:ERROR')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of log entries to return",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="logs_error_count",
            description="Count errors per service over a time window",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "description": "Time range (e.g., '1h', '10m', '30m')",
                        "default": "1h",
                    },
                    "service": {
                        "type": "string",
                        "description": "Filter by service name (optional)",
                    },
                },
            },
        ),
        Tool(
            name="traces_list",
            description="List recent traces for a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name to filter traces",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of traces to return",
                        "default": 10,
                    },
                },
                "required": ["service"],
            },
        ),
        Tool(
            name="traces_get",
            description="Fetch a specific trace by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {
                        "type": "string",
                        "description": "Trace ID to fetch",
                    },
                },
                "required": ["trace_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Call an observability tool."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if name == "logs_search":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 20)
            
            url = f"{settings.victorialogs_url}/select/logsql/query"
            params = {"query": query, "limit": limit}
            
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            
            return [TextContent(type="text", text=resp.text)]
        
        elif name == "logs_error_count":
            time_range = arguments.get("time_range", "1h")
            service = arguments.get("service")
            
            # Build LogsQL query for error count
            base_query = f"_time:{time_range} severity:ERROR"
            if service:
                base_query += f' service.name:"{service}"'
            
            url = f"{settings.victorialogs_url}/select/logsql/query"
            params = {"query": base_query, "limit": 1000}
            
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            
            # Count errors from response
            logs = resp.json() if resp.text.strip() else []
            count = len(logs) if isinstance(logs, list) else 0
            
            return [TextContent(
                type="text",
                text=f"Found {count} error log entries in the last {time_range}"
            )]
        
        elif name == "traces_list":
            service = arguments.get("service")
            limit = arguments.get("limit", 10)
            
            url = f"{settings.victoriatraces_url}/select/jaeger/api/traces"
            params = {"service": service, "limit": limit}
            
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Format trace summary
            traces = data.get("data", [])
            if not traces:
                return [TextContent(type="text", text=f"No traces found for service: {service}")]
            
            summary = []
            for trace in traces[:5]:
                trace_id = trace.get("traceID", "unknown")
                spans = trace.get("spans", [])
                span_count = len(spans)
                summary.append(f"Trace {trace_id[:16]}... ({span_count} spans)")
            
            return [TextContent(
                type="text",
                text=f"Recent traces for {service}:\n" + "\n".join(summary)
            )]
        
        elif name == "traces_get":
            trace_id = arguments.get("trace_id")
            
            url = f"{settings.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
            
            resp = await client.get(url)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Format trace details
            traces = data.get("data", [])
            if not traces:
                return [TextContent(type="text", text=f"Trace {trace_id} not found")]
            
            trace = traces[0]
            spans = trace.get("spans", [])
            
            span_summary = []
            for span in spans:
                span_name = span.get("operationName", "unknown")
                duration = span.get("duration", 0) / 1000  # Convert to ms
                tags = span.get("tags", [])
                error_tag = any(t.get("key") == "error" for t in tags)
                error_marker = " [ERROR]" if error_tag else ""
                span_summary.append(f"  - {span_name}: {duration}ms{error_marker}")
            
            return [TextContent(
                type="text",
                text=f"Trace {trace_id[:16]}...:\n" + "\n".join(span_summary)
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
