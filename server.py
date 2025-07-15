from fastmcp import FastMCP
from algoliasearch.search.client import SearchClientSync
from algoliasearch.search.models import Hit
from pydantic import Field
from dotenv import load_dotenv
import os
from fastmcp.server.dependencies import get_http_headers

# Global variables to hold Algolia configuration: TODO: consider using MCP context variables or a config file
ALGOLIA_APPLICATION_ID = None
ALGOLIA_API_KEY = None
ALGOLIA_INDEX_NAME = None
client = None

mcp = FastMCP("Algolia MCP Server for Index Search", version="0.1.0")


@mcp.tool(
    name="find_products",
    description="Search the product catalog with optional filters and query text"
)
async def algolia_search(
    query: str = Field(default="", description="Search query string"),
    filters: str = Field(default="", description="The filter expression using Algolia's filter syntax (e.g., 'category:Book AND price < 100')"),
    # Parameters for system prompt
    hits_per_page: int = Field(default=3, description="#products per page, Only configurable using system parameters"),
    attributes_to_retrieve: str = Field(default="*", description="Only configurable using system parameters"),
    algolia_index_name: str = Field(default=None, description="Algolia Index Name, only configurable using system parameters"),
) -> list[Hit] | str:
    """Return hits from Algolia search."""
    headers = get_http_headers(include_all=True)
    # print("headers= ", headers)
    authorization = headers.get("authorization")
    authorization_split = authorization.replace("Bearer ", "").split(":")
    algolia_app_id = authorization_split[0]
    algolia_api_key = authorization_split[1]
    # print(f"authorization split= ", authorization_split)
    # TODO: Store the client context as a memory map for each client session
    global ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY, ALGOLIA_INDEX_NAME, client
    if (not ALGOLIA_APPLICATION_ID or not ALGOLIA_API_KEY or 
        ALGOLIA_APPLICATION_ID!= algolia_app_id or ALGOLIA_API_KEY!=algolia_api_key):
        ALGOLIA_APPLICATION_ID = algolia_app_id
        ALGOLIA_API_KEY = algolia_api_key
        client = SearchClientSync(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY)

    ALGOLIA_INDEX_NAME = algolia_index_name
    attributes_to_retrieve_param = [x.strip() for x in attributes_to_retrieve.split(',')] if attributes_to_retrieve else ["*"]
    print ('attributes_to_retrieve_param', attributes_to_retrieve_param)

    response = client.search_single_index(
        index_name=ALGOLIA_INDEX_NAME,
        search_params={
            "query": query,
            "filters": filters,
            "hitsPerPage": hits_per_page,
            "attributesToRetrieve": attributes_to_retrieve_param,
        })
    print("hits=>", response.hits)
    return response.hits if response.hits else "No results found."  # TODO: better handling no results


load_dotenv()

mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp_port = int(os.getenv("MCP_PORT", "8080"))
mcp_path = os.getenv("MCP_PATH", "/mcp")
mcp_transport = os.getenv("MCP_TRANSPORT", "http")
mcp_log_level = os.getenv("MCP_LOG_LEVEL", "info")

print(f"Starting MCP server using {mcp_transport} on {mcp_host}:{mcp_port}{mcp_path} with log level {mcp_log_level}")
mcp.run(
    transport=mcp_transport,
    host=mcp_host,
    port=mcp_port,
    path=mcp_path,
    log_level=mcp_log_level,
)
