# mcps/docker.py
docker_config = {
    "docker": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "mcp-docker-server"]
    }
}
