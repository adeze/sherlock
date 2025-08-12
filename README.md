# Sherlock: Find Usernames Across Social Networks (with MCP Server)

This repository contains the Sherlock project, a powerful command-line tool to hunt down social media accounts by username across a vast number of social networks.

This version has been enhanced with a **Model Context Protocol (MCP) Server**, allowing the Sherlock tool to be used programmatically by AI agents and other MCP-compatible clients.

## Features

- **Sherlock CLI:** The original, powerful command-line tool for username reconnaissance.
- **MCP Server:** A modern, API-like server that exposes Sherlock's functionality as a tool for AI agents.
- **Real-Time Updates:** The MCP server provides real-time progress notifications during searches.
- **Structured Output:** The MCP server returns results in a clean, JSON-friendly format.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. It is recommended to use a virtual environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/your-repo.git
    cd your-repo
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all necessary dependencies from `pyproject.toml`.

## Usage

You can use this project in two ways: as the original Sherlock CLI, or as the new MCP Server.

### Sherlock CLI

To use the command-line tool, first activate the virtual environment created by Poetry:
```bash
poetry shell
```

Then, you can run Sherlock as described in the original documentation:
```bash
sherlock user123
sherlock user1 user2 user3 --site twitter,github
```

### MCP Server

The MCP server allows AI agents and other clients to use Sherlock's functionality as a tool.

**To run the server:**
```bash
poetry run python mcp_server.py
```
The server will start and listen for messages from an MCP client over `stdio`.

**Using the `search_usernames` tool:**

An MCP client can connect to this server and call the `search_usernames` tool with the following parameters:

- `usernames` (List[str]): A list of one or more usernames to search for.
- `sites` (Optional[List[str]]): An optional list of site names to limit the search to.
- `timeout` (int): The timeout in seconds for each website request (default: 60).

The tool will return a JSON object with the found accounts, grouped by username.
