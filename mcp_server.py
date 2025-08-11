import asyncio
import os
from typing import Any, List, Optional

from mcp.server.fastmcp import Context, FastMCP

from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryResult, QueryStatus
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation

# Initialize FastMCP server
mcp = FastMCP(
    "sherlock",
    "A server to find social media accounts by username",
)


class QueryNotifyMCP(QueryNotify):
    """
    A Sherlock notifier that sends progress updates over MCP.
    """

    def __init__(
        self,
        ctx: Context,
        loop: asyncio.AbstractEventLoop,
        total_sites: int,
    ):
        super().__init__()
        self.ctx = ctx
        self.loop = loop
        self.total = total_sites
        self.progress = 0

    def update(self, result: QueryResult):
        """
        Called by Sherlock for each site checked.
        Sends a progress notification over MCP.
        """
        self.progress += 1
        message = (
            f"[{self.progress}/{self.total}] Checking {result.site_name}: "
            f"{result.status.name}"
        )

        # We are in a synchronous function running in a background thread.
        # We need to call the async `report_progress` method on the main
        # event loop in a thread-safe way.
        future = asyncio.run_coroutine_threadsafe(
            self.ctx.report_progress(
                progress=self.progress, total=self.total, message=message
            ),
            self.loop,
        )
        # Wait for the result to avoid any potential race conditions,
        # although for notifications, it's often fire-and-forget.
        future.result(timeout=10)


@mcp.tool()
async def search_usernames(
    ctx: Context,
    usernames: List[str],
    sites: Optional[List[str]] = None,
    timeout: int = 60,
) -> dict:
    """
    Searches for social media accounts by username across social networks.

    Args:
        usernames: A list of one or more usernames to search for.
        sites: An optional list of site names to limit the search to.
        timeout: The timeout in seconds for each website request.
    """
    await ctx.info(f"Starting Sherlock search for: {', '.join(usernames)}")

    data_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "sherlock_project/resources/data.json")
    )

    def get_site_data():
        """Load site data and filter if necessary."""
        sites_info = SitesInformation(data_file_path)
        if sites:
            sites_lower = [s.lower() for s in sites]
            return {
                site.name: site.information
                for site in sites_info
                if site.name.lower() in sites_lower
            }
        else:
            return {site.name: site.information for site in sites_info}

    site_data = await asyncio.to_thread(get_site_data)

    if not site_data:
        await ctx.warning("No sites found for the given criteria.")
        return {"error": "No sites found to search. Please check the site names."}

    # Get the current event loop to pass to the notifier.
    loop = asyncio.get_running_loop()
    query_notify = QueryNotifyMCP(ctx, loop, total_sites=len(site_data))

    def run_searches():
        """Run Sherlock for all usernames."""
        results = {}
        for username in usernames:
            # The sherlock function is synchronous and will call the
            # notifier's `update` method from within this thread.
            user_results = sherlock(
                username,
                site_data,
                query_notify,
                timeout=timeout,
            )
            results[username] = user_results
        return results

    all_results = await asyncio.to_thread(run_searches)

    # Format the final result into a structured dictionary.
    final_results = {}
    for username, results in all_results.items():
        found_accounts = []
        for site_name, result_details in results.items():
            if result_details["status"].status == QueryStatus.CLAIMED:
                found_accounts.append(
                    {"site_name": site_name, "url": result_details["url_user"]}
                )
        if found_accounts:
            final_results[username] = found_accounts

    if not final_results:
        await ctx.info("Search complete. No accounts found.")
        return {"status": "No accounts found."}

    await ctx.info(f"Search complete. Found accounts for {len(final_results)} user(s).")
    return final_results


if __name__ == "__main__":
    # This allows the server to be run directly from the command line.
    # It will communicate with the MCP client over standard I/O.
    mcp.run(transport="stdio")
