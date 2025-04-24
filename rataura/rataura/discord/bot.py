"""
Discord bot module for the Rataura application.
"""

import logging
import discord
from discord.ext import commands
from rataura.config import settings
from rataura.llm.function_tools import process_message

# Configure logging
logger = logging.getLogger(__name__)

# Create a Discord bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    """
    logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guilds")
    
    # Set the bot's activity
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name="EVE Online queries"
    )
    await bot.change_presence(activity=activity)


@bot.event
async def on_message(message):
    """
    Event handler for when a message is received.
    
    Args:
        message (discord.Message): The message that was received.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)
    
    # Check if the bot is mentioned or the message is a DM
    is_mentioned = bot.user in message.mentions
    is_dm = isinstance(message.channel, discord.DMChannel)
    
    if is_mentioned or is_dm:
        # Get the message content without the mention
        content = message.content
        if is_mentioned:
            content = content.replace(f"<@{bot.user.id}>", "").strip()
            content = content.replace(f"<@!{bot.user.id}>", "").strip()
        
        # Show typing indicator
        async with message.channel.typing():
            # Process the message with the LLM
            response = await process_message(content)
            
            # Send the response
            await message.reply(response)


@bot.command(name="help")
async def help_command(ctx):
    """
    Command to show help information.
    
    Args:
        ctx (commands.Context): The command context.
    """
    embed = discord.Embed(
        title="Rataura - EVE Online Assistant",
        description="I'm a bot that can help you with EVE Online information. Just mention me or DM me with your question!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Examples",
        value=(
            "- @Rataura What is the current price of PLEX in Jita?\n"
            "- @Rataura Tell me about the Amarr faction\n"
            "- @Rataura What skills do I need for a Raven?"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Authentication",
        value=(
            "Some queries require authentication with your EVE Online account. "
            "Use the `!login` command to authenticate."
        ),
        inline=False
    )
    
    embed.set_footer(text="Powered by EVE Online ESI API")
    
    await ctx.send(embed=embed)


@bot.command(name="login")
async def login_command(ctx):
    """
    Command to authenticate with EVE Online.
    
    Args:
        ctx (commands.Context): The command context.
    """
    # TODO: Implement EVE Online authentication
    await ctx.send("EVE Online authentication is not yet implemented.")


def start_bot():
    """
    Start the Discord bot.
    """
    logger.info("Starting Discord bot...")
    bot.run(settings.discord_token)
