# freqtrade_mcp.py
import os
import sys
from typing import List, AsyncIterator, Dict, Any
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP, Context

# Import Freqtrade REST client
from freqtrade_client.ft_rest_client import FtRestClient

# Configuration loaded from environment variables
FREQTRADE_API_URL = os.getenv("FREQTRADE_API_URL", "http://127.0.0.1:8080")
USERNAME = os.getenv("FREQTRADE_USERNAME", "Freqtrader")
PASSWORD = os.getenv("FREQTRADE_PASSWORD", "SuperSecret1!")

# Lifecycle management for the Freqtrade client
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage the lifecycle of the Freqtrade REST client."""
    client = FtRestClient(FREQTRADE_API_URL, USERNAME, PASSWORD)
    try:
        # Test API connectivity
        if client.ping():
            print("Connected to Freqtrade API", file=sys.stderr)
        else:
            raise Exception("Failed to connect to Freqtrade API")
        yield {"client": client}
    finally:
        print("Freqtrade API client closed", file=sys.stderr)

# Initialize MCP server (only once, with lifespan)
mcp = FastMCP("FreqtradeMCP", dependencies=["freqtrade-client"], lifespan=app_lifespan)

# Tools (Converted from resources and actions)
@mcp.tool()
def fetch_market_data(pair: str, timeframe: str, ctx: Context) -> str:
    """
    Fetch OHLCV data for a specified trading pair and timeframe.

    Parameters:
        pair (str): Trading pair (e.g., "BTC/USDT").
        timeframe (str): Timeframe for the data (e.g., "1h", "5m").
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response containing OHLCV data, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    print(f"Fetching market data for {pair} with timeframe {timeframe}", file=sys.stderr)
    return str(client.pair_candles(pair=pair, timeframe=timeframe))

@mcp.tool()
def fetch_bot_status(ctx: Context) -> str:
    """
    Retrieve the current status of open trades.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with open trade status, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.status())

@mcp.tool()
def fetch_profit(ctx: Context) -> str:
    """
    Get profit summary for the trading bot.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with profit summary, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.profit())

@mcp.tool()
def fetch_balance(ctx: Context) -> str:
    """
    Fetch the account balance.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with account balance, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.balance())

@mcp.tool()
def fetch_performance(ctx: Context) -> str:
    """
    Retrieve trading performance metrics.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with performance metrics, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.performance())

@mcp.tool()
def fetch_whitelist(ctx: Context) -> str:
    """
    Get the current whitelist of trading pairs.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with whitelist data, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.whitelist())

@mcp.tool()
def fetch_blacklist(ctx: Context) -> str:
    """
    Get the current blacklist of trading pairs.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with blacklist data, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.blacklist())

@mcp.tool()
def fetch_trades(ctx: Context) -> str:
    """
    Fetch the history of closed trades.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with trade history, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.trades())

@mcp.tool()
def fetch_config(ctx: Context) -> str:
    """
    Retrieve the current bot configuration.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with configuration data, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.config())

@mcp.tool()
def fetch_locks(ctx: Context) -> str:
    """
    Get the current trade locks.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with trade locks data, or None if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    return str(client.locks())

@mcp.tool()
def place_trade(pair: str, side: str, stake_amount: float, ctx: Context) -> str:
    """
    Place a trade (buy or sell) with the specified pair and amount.

    Parameters:
        pair (str): Trading pair (e.g., "BTC/USDT").
        side (str): Trade direction, either "buy" or "sell".
        stake_amount (float): Amount to trade in the stake currency.
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with trade result, or error message if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    if side.lower() not in ["buy", "sell"]:
        return str({"error": "Side must be 'buy' or 'sell'"})
    response = client.forcebuy(pair=pair, stake_amount=stake_amount) if side.lower() == "buy" else \
               client.forcesell(pair=pair, amount=stake_amount)
    print(f"Trade placed: {side} {stake_amount} of {pair}", file=sys.stderr)
    return str(response)

@mcp.tool()
def start_bot(ctx: Context) -> str:
    """
    Start the Freqtrade bot.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response or success message, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.start_bot()
    print("Freqtrade bot started", file=sys.stderr)
    return str(response)

@mcp.tool()
def stop_bot(ctx: Context) -> str:
    """
    Stop the Freqtrade bot.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response or success message, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.stop_bot()
    print("Freqtrade bot stopped", file=sys.stderr)
    return str(response)

@mcp.tool()
def reload_config(ctx: Context) -> str:
    """
    Reload the bot configuration.

    Parameters:
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response or success message, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.reload_config()
    print("Configuration reloaded", file=sys.stderr)
    return str(response)

@mcp.tool()
def add_blacklist(pair: str, ctx: Context) -> str:
    """
    Add a pair to the blacklist.

    Parameters:
        pair (str): Trading pair to blacklist (e.g., "ETH/USDT").
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with updated blacklist, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.add_blacklist(pair)
    print(f"Added {pair} to blacklist", file=sys.stderr)
    return str(response)

@mcp.tool()
def delete_blacklist(pair: str, ctx: Context) -> str:
    """
    Remove a pair from the blacklist.

    Parameters:
        pair (str): Trading pair to remove from blacklist (e.g., "ETH/USDT").
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with updated blacklist, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.delete_blacklist(pair)
    print(f"Removed {pair} from blacklist", file=sys.stderr)
    return str(response)

@mcp.tool()
def delete_lock(lock_id: int, ctx: Context) -> str:
    """
    Delete a specific trade lock by ID.

    Parameters:
        lock_id (int): ID of the trade lock to delete.
        ctx (Context): MCP context object for logging and client access.

    Returns:
        str: Stringified JSON response with updated locks, or error if failed.
    """
    client: FtRestClient = ctx.request_context.lifespan_context["client"]
    response = client.delete_lock(lock_id)
    print(f"Deleted lock with ID {lock_id}", file=sys.stderr)
    return str(response)

# Prompts (Updated to return list of dicts instead of Message objects)
@mcp.prompt()
def analyze_trade(pair: str, timeframe: str, ctx: Context) -> List[Dict[str, Any]]:
    """Generate a prompt to analyze a trading pair's performance."""
    market_data = fetch_market_data(pair, timeframe, ctx)
    return [
        {"role": "user", "content": f"Analyze the recent performance of {pair} over {timeframe}."},
        {"role": "user", "content": f"Market data: {market_data}"},
        {"role": "assistant", "content": f"I'll analyze the market data for {pair} and provide insights."}
    ]

@mcp.prompt()
def trading_strategy(ctx: Context) -> str:
    """Generate a prompt for suggesting a trading strategy."""
    return "Based on the current bot status, profit, and market conditions, suggest a trading strategy."

# Run the server
if __name__ == "__main__":
    import sys
    try:
        print(f"Starting Freqtrade MCP server...", file=sys.stderr)
        print(f"API URL: {FREQTRADE_API_URL}", file=sys.stderr)
        print(f"Username: {USERNAME}", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
