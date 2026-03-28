"""Entry point for running mcp_obs as a module."""

import asyncio

from mcp_obs.server import main


if __name__ == "__main__":
    asyncio.run(main())
