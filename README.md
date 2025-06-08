# mcp-bonusly

[![Available on Smithery](https://img.shields.io/badge/Available%20on-Smithery-blue?style=flat&logo=smithery)](https://smithery.ai/)

**Comprehensive MCP server for Bonusly employee recognition platform**

MCP server to interact with Bonusly API, enabling management of employee recognition bonuses through Claude and other MCP clients.

**🚀 Available on [Smithery](https://smithery.ai/) for easy local installation!**

## Table of Contents

* [Quick Start](#quick-start)
* [Features](#features)
* [Installation](#installation)
* [Setup](#setup)
* [Available Tools](#available-tools)
* [Example Prompts](#example-prompts)
* [Development](#development)
* [License](#license)

## Quick Start

### Quick Installation

```bash
git clone https://github.com/ajramos/mcp-bonusly
cd mcp-bonusly
uv sync
```

### Quick Setup

1. Get your Bonusly API token from https://bonus.ly/api
2. Create a `.env` file with your token:
   ```
   BONUSLY_API_TOKEN=your_api_token_here
   ```
3. Configure Claude Desktop to use the server

## Features

### ✨ Complete Bonus Management
- **List bonuses** with advanced filtering (including new user_email parameter for team analysis)
- **Create new bonuses** with validation
- **Retrieve bonus details** for specific bonuses

### 🔍 Advanced Filtering
- Filter by date range
- Filter by giver email
- Filter by receiver email
- Filter by hashtags
- Limit number of results

### 🛡️ Security
- Secure authentication with API token
- Input data validation
- Robust error handling

## Installation

### Option 1: Install from Smithery (Recommended)

This MCP is available on [Smithery](https://smithery.ai/) as a local installation:

1. Visit [Smithery](https://smithery.ai/)
2. Search for "mcp-bonusly"
3. Follow the installation instructions for local MCPs
4. Configure your Bonusly API token (see Setup section below)

### Option 2: Manual Installation with uv

```bash
git clone https://github.com/ajramos/mcp-bonusly
cd mcp-bonusly
uv sync
```

### Option 3: Manual Installation with pip

```bash
git clone https://github.com/ajramos/mcp-bonusly
cd mcp-bonusly
pip install -e .
```

## Setup

### 1. Get Bonusly API Token

1. Go to https://bonus.ly/api
2. Sign in to your Bonusly account
3. Create a new API token
4. Copy the generated token

### 2. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
BONUSLY_API_TOKEN=your_api_token_here
```

### 3. Configure Claude Desktop

Add this configuration to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "mcp-bonusly": {
      "command": "uv",
      "args": [
        "--directory", 
        "/full/path/to/mcp-bonusly",
        "run",
        "mcp-bonusly"
      ],
      "env": {
        "BONUSLY_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## Available Tools

### 🎁 `list_bonuses`
List bonuses with optional filters.

**Parameters:**
- `limit` (optional): Number of bonuses to return (1-100, default: 20)
- `start_date` (optional): Start date (format: YYYY-MM-DD)
- `end_date` (optional): End date (format: YYYY-MM-DD)
- `giver_email` (optional): Giver's email address
- `receiver_email` (optional): Receiver's email address
- `user_email` (optional): User's email address (bonuses given or received by this user). **Recommended for team analysis: search for each team member individually to ensure complete coverage.**
- `hashtag` (optional): Hashtag to filter by (e.g., #teamwork)
- `include_children` (optional): Include bonus replies

### 🆕 `create_bonus`
Create a new recognition bonus.

**Parameters:**
- `giver_email` (optional): Giver's email address (admin only, regular users send bonuses in their own name)
- `reason` (required): Bonus reason (e.g., "+10 @user for #teamwork")
- `parent_bonus_id` (optional): Parent bonus ID for replies

### 🔍 `get_bonus`
Get details of a specific bonus.

**Parameters:**
- `bonus_id` (required): ID of the bonus to retrieve

## Example Prompts

### List Recent Bonuses
```
"Show me the last 10 bonuses given"
```

### Create a Bonus
```
"Create a 5-point bonus for john@company.com for excellent work on the project with #teamwork"
```

### Search Bonuses by Hashtag
```
"Show me all bonuses with hashtag #innovation from last month"
```

### Get Bonus Details
```
"Get details for bonus with ID 24abcdef1234567890abcdef"
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/ajramos/mcp-bonusly
cd mcp-bonusly
uv sync
uv run mcp-bonusly
```

### Debugging with MCP Inspector

For the best debugging experience, we recommend using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-bonusly run mcp-bonusly
```

### View Server Logs

```bash
# macOS
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-bonusly.log

# Linux 
tail -n 20 -f ~/.config/Claude/logs/mcp-server-mcp-bonusly.log

# Windows
Get-Content "$env:APPDATA\Claude\logs\mcp-server-mcp-bonusly.log" -Wait -Tail 20
```

## Project Structure

```
mcp-bonusly/
├── src/
│   └── mcp_bonusly/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── client.py          # Bonusly API client
│       ├── models.py          # Pydantic models
│       └── exceptions.py      # Custom exceptions
├── tests/                     # Tests (coming soon)
├── .env.example              # Environment variables example
├── .gitignore
├── README.md
├── pyproject.toml
└── LICENSE
```

## Security

- All credentials are handled through environment variables
- API token is stored securely
- No data is sent to third parties except Bonusly API
- Input validation on all operations

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues:

1. **Check the logs** using the debugging instructions above
2. **Verify your API token** in the `.env` file
3. **Open an issue** with:
   - Your operating system
   - Python version
   - Error messages or logs
   - Steps to reproduce the issue

## About Bonusly

Bonusly is an employee recognition platform that enables companies to create a culture of appreciation and engagement. Employees can give points to each other with personalized messages and hashtags that reflect company values.

---

**Created with ❤️ by Angel Ramos** 