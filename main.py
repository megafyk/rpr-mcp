import contextlib
import os
from atlassian import Bitbucket
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

load_dotenv()

mcp = FastMCP()


bitbucket = Bitbucket(
    url=os.getenv("BITBUCKET_URL"),
    username=os.getenv("BITBUCKET_USERNAME"),
    password=os.getenv("BITBUCKET_PASSWORD"),
)


@mcp.tool()
def get_prs(project: str, repo: str) -> str:
    """
    Get pull requests from bitbucket repository for a given project and repository.
    Args:
        project (str): The project key.
        repo (str): The repository slug.
    """
    try:
        prs = bitbucket.get_pull_requests(
            project, repo, state="OPEN", order="newest", limit=100, start=0
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
        return f"Error fetching pull requests: {str(e)}"


# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/rpr", mcp.streamable_http_app())
