import contextlib
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import logging
import httpx
import base64

load_dotenv()

mcp = FastMCP()

log = logging.getLogger(__name__)


def get_bitbucket_headers() -> dict:
    """
    Get headers for Bitbucket API requests.
    Returns:
        dict: Headers for the request.
    """
    username = os.getenv("BITBUCKET_USERNAME")
    password = os.getenv("BITBUCKET_PASSWORD")
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode("ascii")

    return {
        "Accept": "application/json",
        "Authorization": f"Basic {base64_string}",
    }


@mcp.tool(
    "Get open pull requests from bitbucket repository for a given project and repository."
)
async def get_pull_requests(project: str, repository: str) -> str:
    """
    Get open pull requests from bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
    """
    try:
        url = f"{os.getenv('BITBUCKET_URL')}/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests?state={'OPEN'}&start={0}&limit={99999}"
        headers = get_bitbucket_headers()
        response: httpx.Response = None
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()  # Raises an HTTPStatusError for bad responses (4xx or 5xx)

        if not response.json().get("values"):
            return "No pull requests found."

        pull_requests = response.json().get("values", [])

        res = []
        for pr in pull_requests:
            pr_info = (
                f"ID: {pr.get('id', None)}\\n"
                f"Title: {pr.get('title', None)}\\n"
                f"State: {pr.get('state', None)}\\n"
                f"Author: {pr.get('author', {}).get('user', {}).get('displayName', None)}\\n"
            )
            res.append(pr_info)
        return "\\n".join(res)
    except httpx.HTTPStatusError as e:
        log.error(
            f"HTTP error fetching pull requests: {e.response.status_code} - {e.response.text}"
        )
        return f"Error fetching pull requests: {e.response.status_code}"
    except httpx.RequestError as e:
        log.error(f"Request error fetching pull requests: {str(e)}")
        return f"Error fetching pull requests: {str(e)}"
    except Exception as e:
        log.error(f"Error processing pull requests: {str(e)}")
        return f"Error processing pull requests: {str(e)}"


@mcp.tool(
    "Get change files from pull requests in a bitbucket repository for a given project and repository."
)
async def get_pull_requests_changes(
    project: str, repository: str, pull_request_id: int
) -> str:
    """
    Get change files from pull requests in a bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
        pull_request_id (int): The pull request ID.
    """
    try:
        url = f"{os.getenv('BITBUCKET_URL')}/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pull_request_id}/changes?start{0}&limit{99999}"
        headers = get_bitbucket_headers()
        response: httpx.Response = None
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()  # Raises an HTTPStatusError for bad responses (4xx or 5xx)

        if not response.json().get("values"):
            return "No changes found in the pull request."

        changes = response.json().get("values", [])

        res = []
        for change in changes:
            change_info = (
                f"File: {change.get('path', {}).get('toString', None)}\\n"
                f"Type: {change.get('type', None)}\\n"
            )
            res.append(change_info)
        return "\\n".join(res)
    except httpx.HTTPStatusError as e:
        log.error(
            f"HTTP error fetching pull request changes: {e.response.status_code} - {e.response.text}"
        )
        return f"Error fetching pull request changes: {e.response.status_code}"
    except httpx.RequestError as e:
        log.error(f"Request error fetching pull request changes: {str(e)}")
        return f"Error fetching pull request changes: {str(e)}"
    except Exception as e:
        log.error(f"Error processing pull request changes: {str(e)}")
        return f"Error processing pull request changes: {str(e)}"


@mcp.tool(
    "Get file diff from pull request in a bitbucket repository for a given project and repository."
)
async def get_file_diff(
    project: str, repository: str, pull_request_id: int, path: str
) -> str:
    """
    Get file diff from pull request in a bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
        pull_request_id (int): The pull request ID.
        path (str): The file path in the repository.
    """
    try:
        url = f"{os.getenv('BITBUCKET_URL')}/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pull_request_id}/diff/{path}"
        headers = get_bitbucket_headers()
        headers.set("Accept", "text/plain")
        response: httpx.Response = None
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        response.raise_for_status()  # Raises an HTTPStatusError for bad responses (4xx or 5xx)

        return response.text
    except httpx.HTTPStatusError as e:
        log.error(
            f"HTTP error fetching file diff: {e.response.status_code} - {e.response.text}"
        )
        return f"Error fetching file diff: {e.response.status_code}"
    except httpx.RequestError as e:
        log.error(f"Request error fetching file diff: {str(e)}")
        return f"Error fetching file diff: {str(e)}"


# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/rpr", mcp.streamable_http_app())
