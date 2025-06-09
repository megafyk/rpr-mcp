import contextlib
import os
from atlassian import Bitbucket
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import logging

load_dotenv()

mcp = FastMCP()

log = logging.getLogger(__name__)

bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD"),
)


@mcp.tool(
    "Get pull requests from bitbucket repository for a given project and repository."
)
def get_pull_requests(project: str, repository: str) -> str:
    """
    Get pull requests from bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
    """
    try:
        prs = bitbucket.get_pull_requests(
            project, repository, state="OPEN", order="newest", limit=100, start=0
        )
        if not prs:
            return "No open pull requests found."
        res = []
        for pr in prs:
            pr_info = (
                f"ID: {pr.get('id', None)}\n"
                f"Title: {pr.get('title', None)}\n"
                f"Description: {pr.get('description', None)}\n"
                f"Source: {pr.get('fromRef', {}).get('id', None)}\n"
                f"Target: {pr.get('toRef', {}).get('id', None)}\n"
            )
            res.append(pr_info)
        return "\n".join(res)
    except Exception as e:
        log.error(f"Error fetching pull requests: {str(e)}")
        return f"Error fetching pull requests: {str(e)}"


@mcp.tool(
    "Get changes from pull requests in a bitbucket repository for a given project and repository."
)
def get_pull_requests_changes(
    project: str, repository: str, pull_request_id: int
) -> str:
    """
    Get changes from pull requests in a bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
        pull_request_id (int): The pull request ID.
    """
    try:
        changes = bitbucket.get_pull_requests_changes(
            project, repository, pull_request_id
        )
        if not changes:
            return "No changes found in the pull request."
        res = []
        for change in changes:
            change_info = (
                f"File: {change.get('path', {}).get('toString', None)}\n"
                f"Type: {change.get('type', None)}\n"
                f"Lines Added: {change.get('linesAdded', 0)}\n"
                f"Lines Removed: {change.get('linesRemoved', 0)}\n"
            )
            res.append(change_info)
        return "\n".join(res)
    except Exception as e:
        log.error(f"Error fetching pull request changes: {str(e)}")
        return f"Error fetching pull request changes: {str(e)}"


@mcp.tool("Get changelog from bitbucket repository for a given project and repository.")
def get_changelog(
    project: str, repository: str, ref_from: str, ref_to: str, limit=99999
) -> str:
    """
    Get changelog from bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repository (str): The repository slug.
        ref_from (str): The starting reference (e.g., branch or tag).
        ref_to (str): The ending reference (e.g., branch or tag).
        limit (int): The maximum number of changes to return.
    """
    try:
        changelog = bitbucket.get_changelog(
            project, repository, ref_from, ref_to, limit=limit
        )
        if not changelog:
            return "No changes found."
        return "\n".join(changelog)
    except Exception as e:
        log.error(f"Error fetching changelog: {str(e)}")
        return f"Error fetching changelog: {str(e)}"


# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/rpr", mcp.streamable_http_app())
