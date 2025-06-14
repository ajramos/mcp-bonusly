"""
MCP server for Bonusly employee recognition platform.

This server provides tools to interact with the Bonusly API for managing
employee recognition bonuses through the Model Context Protocol.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Sequence

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

from .client import BonuslyClient
from .models import ListBonusesRequest, CreateBonusRequest, GetBonusRequest
from . import __version__
from .exceptions import (
    BonuslyError, BonuslyAuthenticationError, BonuslyAPIError,
    BonuslyNotFoundError, BonuslyConfigurationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("mcp-bonusly")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools for Bonusly operations.
    
    Returns:
        List of available tools
    """
    return [
        Tool(
            name="list_bonuses",
            description="List bonuses with optional filtering by date range, users, or hashtags. IMPORTANT: For team-specific analysis, use 'user_email' for each team member individually instead of global searches with 'limit' to ensure complete team coverage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of bonuses to return (1-100, default: 20)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for filtering (YYYY-MM-DD format)",
                        "pattern": r"^\d{4}-\d{2}-\d{2}$"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for filtering (YYYY-MM-DD format)",
                        "pattern": r"^\d{4}-\d{2}-\d{2}$"
                    },
                    "giver_email": {
                        "type": "string",
                        "description": "Filter by giver's email address",
                        "format": "email"
                    },
                    "receiver_email": {
                        "type": "string",
                        "description": "Filter by receiver's email address",
                        "format": "email"
                    },
                    "user_email": {
                        "type": "string",
                        "description": "Filter by user's email address (bonuses given or received by this user). RECOMMENDED for team analysis: search for each team member individually to ensure complete coverage.",
                        "format": "email"
                    },
                    "hashtag": {
                        "type": "string",
                        "description": "Filter by hashtag (e.g., 'teamwork' or '#teamwork')"
                    },
                    "include_children": {
                        "type": "boolean",
                        "description": "Include bonus replies/children",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_bonus",
            description="Create a new recognition bonus for an employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "giver_email": {
                        "type": "string",
                        "description": "Email address of the person giving the bonus (admin only, optional)",
                        "format": "email"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the bonus (e.g., '+10 @john.doe for #teamwork on the project')"
                    },
                    "parent_bonus_id": {
                        "type": "string",
                        "description": "Optional parent bonus ID for creating a reply/child bonus"
                    }
                },
                "required": ["reason"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_bonus",
            description="Retrieve details of a specific bonus by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "bonus_id": {
                        "type": "string",
                        "description": "The ID of the bonus to retrieve"
                    }
                },
                "required": ["bonus_id"],
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls for Bonusly operations.
    
    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool
        
    Returns:
        List of text content with results
    """
    try:
        # Initialize Bonusly client
        client = BonuslyClient()
        
        if name == "list_bonuses":
            return await _handle_list_bonuses(client, arguments)
        elif name == "create_bonus":
            return await _handle_create_bonus(client, arguments)
        elif name == "get_bonus":
            return await _handle_get_bonus(client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except BonuslyConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Configuration Error: {e}\n\n"
                 "Please ensure your BONUSLY_API_TOKEN environment variable is set correctly."
        )]
    except BonuslyAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Authentication Error: {e}\n\n"
                 "Please check your Bonusly API token is valid and has the necessary permissions."
        )]
    except BonuslyNotFoundError as e:
        logger.error(f"Not found error: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Not Found: {e}"
        )]
    except BonuslyAPIError as e:
        logger.error(f"API error: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Bonusly API Error: {e}"
        )]
    except Exception as e:
        logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ Unexpected error: {e}"
        )]
    finally:
        # Clean up client if it exists
        if 'client' in locals():
            client.close()


async def _handle_list_bonuses(client: BonuslyClient, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle list_bonuses tool call."""
    try:
        # Create request object with validation
        request = ListBonusesRequest(**arguments)
        
        # Get bonuses from API
        bonuses = client.list_bonuses(request)
        
        if not bonuses:
            return [TextContent(
                type="text",
                text="No bonuses found matching the specified criteria."
            )]
        
        # Format response
        result_text = f"📋 **Found {len(bonuses)} bonus(es)**\n\n"
        
        for i, bonus in enumerate(bonuses, 1):
            result_text += f"**{i}. Bonus #{bonus.id}**\n"
            result_text += f"   💰 Amount: {bonus.amount_with_currency}\n"
            result_text += f"   👤 Giver: {bonus.giver.display_name} ({bonus.giver.email})\n"
            
            if bonus.receiver:
                result_text += f"   🎯 Receiver: {bonus.receiver.display_name} ({bonus.receiver.email})\n"
            elif bonus.receivers:
                receivers = ", ".join([f"{r.display_name}" for r in bonus.receivers[:3]])
                if len(bonus.receivers) > 3:
                    receivers += f" and {len(bonus.receivers) - 3} more"
                result_text += f"   🎯 Receivers: {receivers}\n"
            
            result_text += f"   📅 Date: {bonus.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"   💬 Reason: {bonus.reason}\n"
            
            if bonus.child_count > 0:
                result_text += f"   💭 Replies: {bonus.child_count}\n"
            
            result_text += "\n"
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"Error in list_bonuses: {e}")
        raise


async def _handle_create_bonus(client: BonuslyClient, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle create_bonus tool call."""
    try:
        # Create request object with validation
        request = CreateBonusRequest(**arguments)
        
        # Create bonus via API
        bonus = client.create_bonus(request)
        
        # Format response
        result_text = f"✅ **Bonus Created Successfully!**\n\n"
        result_text += f"🆔 **Bonus ID:** {bonus.id}\n"
        result_text += f"💰 **Amount:** {bonus.amount_with_currency}\n"
        result_text += f"👤 **Giver:** {bonus.giver.display_name} ({bonus.giver.email})\n"
        
        if bonus.receiver:
            result_text += f"🎯 **Receiver:** {bonus.receiver.display_name} ({bonus.receiver.email})\n"
        elif bonus.receivers:
            receivers = ", ".join([f"{r.display_name}" for r in bonus.receivers])
            result_text += f"🎯 **Receivers:** {receivers}\n"
        
        result_text += f"📅 **Date:** {bonus.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result_text += f"💬 **Reason:** {bonus.reason}\n"
        
        if bonus.parent_bonus_id:
            result_text += f"↩️ **Reply to:** {bonus.parent_bonus_id}\n"
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"Error in create_bonus: {e}")
        raise


async def _handle_get_bonus(client: BonuslyClient, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_bonus tool call."""
    try:
        # Create request object with validation
        request = GetBonusRequest(**arguments)
        
        # Get bonus from API
        bonus = client.get_bonus(request)
        
        # Format response
        result_text = f"🎁 **Bonus Details**\n\n"
        result_text += f"🆔 **ID:** {bonus.id}\n"
        result_text += f"💰 **Amount:** {bonus.amount_with_currency}\n"
        result_text += f"👤 **Giver:** {bonus.giver.display_name} ({bonus.giver.email})\n"
        
        if bonus.receiver:
            result_text += f"🎯 **Receiver:** {bonus.receiver.display_name} ({bonus.receiver.email})\n"
        elif bonus.receivers:
            receivers = ", ".join([f"{r.display_name} ({r.email})" for r in bonus.receivers])
            result_text += f"🎯 **Receivers:** {receivers}\n"
        
        result_text += f"📅 **Created:** {bonus.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result_text += f"💬 **Reason:** {bonus.reason}\n"
        
        if bonus.reason_html and bonus.reason_html != bonus.reason:
            result_text += f"🌐 **HTML Reason:** {bonus.reason_html}\n"
        
        if bonus.value:
            result_text += f"🏷️ **Value/Hashtag:** {bonus.value}\n"
        
        if bonus.parent_bonus_id:
            result_text += f"↩️ **Reply to:** {bonus.parent_bonus_id}\n"
        
        if bonus.child_count > 0:
            result_text += f"💭 **Replies:** {bonus.child_count}\n"
        
        result_text += f"📱 **Via:** {bonus.via}\n"
        result_text += f"👥 **Family Amount:** {bonus.family_amount}\n"
        
        # Add giver details
        result_text += f"\n**👤 Giver Details:**\n"
        result_text += f"   • Name: {bonus.giver.first_name} {bonus.giver.last_name}\n"
        result_text += f"   • Username: @{bonus.giver.username}\n"
        result_text += f"   • Giving Balance: {bonus.giver.giving_balance_with_currency}\n"
        result_text += f"   • Lifetime Earnings: {bonus.giver.lifetime_earnings_with_currency}\n"
        
        if bonus.giver.country:
            result_text += f"   • Country: {bonus.giver.country}\n"
        if bonus.giver.time_zone:
            result_text += f"   • Timezone: {bonus.giver.time_zone}\n"
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"Error in get_bonus: {e}")
        raise


async def async_main():
    """Async main entry point for the MCP server."""
    # Configure logging level from environment
    log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
    
    logger.info("Starting Bonusly MCP server...")
    
    # Check for API token
    if not os.getenv("BONUSLY_API_TOKEN"):
        logger.error("BONUSLY_API_TOKEN environment variable is not set!")
        sys.exit(1)
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-bonusly",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )


def main():
    """Main entry point for the MCP server (non-async wrapper)."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
