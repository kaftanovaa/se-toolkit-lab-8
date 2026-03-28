#!/usr/bin/env python3
"""
Nanobot gateway entrypoint for Docker.

Resolves environment variables into config.json at runtime,
then execs into `nanobot gateway`.
"""

import json
import os
import sys
from pathlib import Path


def main():
    # Paths
    config_dir = Path(__file__).parent
    config_path = config_dir / "config.json"
    resolved_path = config_dir / "config.resolved.json"
    workspace_dir = config_dir / "workspace"

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Override from environment variables
    # LLM provider settings
    if llm_api_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = llm_api_key

    if llm_api_base := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = llm_api_base

    if llm_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = llm_model

    # Gateway settings
    if gateway_host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config.setdefault("gateway", {})["host"] = gateway_host

    if gateway_port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # Webchat channel settings
    if webchat_host := os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS"):
        config.setdefault("channels", {}).setdefault("webchat", {})["host"] = webchat_host

    if webchat_port := os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT"):
        config.setdefault("channels", {}).setdefault("webchat", {})["port"] = int(webchat_port)

    # MCP LMS server env vars
    if lms_backend_url := os.environ.get("NANOBOT_LMS_BACKEND_URL"):
        config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("lms", {}).setdefault("env", {})["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url

    if lms_api_key := os.environ.get("NANOBOT_LMS_API_KEY"):
        config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("lms", {}).setdefault("env", {})["NANOBOT_LMS_API_KEY"] = lms_api_key

    # MCP Webchat server env vars
    if webchat_ui_url := os.environ.get("NANOBOT_WEBCCHAT_UI_RELAY_URL"):
        config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("webchat", {}).setdefault("env", {})["NANOBOT_WEBCCHAT_UI_RELAY_URL"] = webchat_ui_url

    if webchat_token := os.environ.get("NANOBOT_WEBCCHAT_TOKEN"):
        config.setdefault("tools", {}).setdefault("mcpServers", {}).setdefault("webchat", {}).setdefault("env", {})["NANOBOT_WEBCCHAT_TOKEN"] = webchat_token

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Exec into nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", str(resolved_path), "--workspace", str(workspace_dir)])


if __name__ == "__main__":
    main()
