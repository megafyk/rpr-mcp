# RPR-MCP

A FastAPI-based Model Context Protocol (MCP) server for Bitbucket repository integration.

## Features

- Get open pull requests from Bitbucket repositories
- View changed files in pull requests
- Get file diffs from pull requests
- RESTful API endpoints
- MCP server capabilities

## Requirements

- Python 3.11+
- Docker (optional)

## Environment Variables

Create a `.env` file with the following variables:

```env
BITBUCKET_URL=https://your-bitbucket-server.com
BITBUCKET_USERNAME=your-username
BITBUCKET_PASSWORD=your-password
```

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or use the convenience script
./docker.sh run
```

### Local Development

```bash
# Install dependencies
uv sync

# Run the application
uv run fastapi run main.py --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /api/v1/pr` - Get open pull requests
- `GET /api/v1/pr/change` - Get pull request changes
- `GET /api/v1/pr/diff` - Get file diff from pull request
- `/rpr` - MCP streamable HTTP app

## Usage Example

```bash
# Get open pull requests
curl "http://localhost:8000/api/v1/pr?project=PROJECT_KEY&repository=repo-name"

# Get file diff
curl "http://localhost:8000/api/v1/pr/diff?project=PROJECT_KEY&repository=repo-name&pull_request_id=123&path=src/file.py"
```

## Docker Commands

```bash
./docker.sh build    # Build image
./docker.sh run      # Run container
./docker.sh stop     # Stop container
./docker.sh logs     # View logs
./docker.sh shell    # Open shell
./docker.sh clean    # Remove container and image
```

## License

MIT