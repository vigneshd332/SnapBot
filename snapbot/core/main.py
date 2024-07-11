import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import List, Union

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv("snapbot/data/.env")  # Load environment variables

from shared.handlers import ConfigLoader

config = ConfigLoader()

# Configure logger
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

MAX_BYTES = 1048576  # 1 MiB
BACKUP_COUNT = 5  # Rotate through 5 files

formatter = logging.Formatter(
    fmt="[%(levelname)s] [%(asctime)s] - %(message)s [%(filename)s (%(lineno)s)]",
    datefmt="%Y/%m/%d | %I:%M:%S %p",
)

info_handler = RotatingFileHandler(
    filename="snapbot/data/logs/events.log",
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
)
# Only record the levels INFO and WARNING
info_handler.addFilter(
    lambda record: record.levelno < logging.ERROR and record.levelno != logging.DEBUG
)
info_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(
    filename="snapbot/data/logs/errors.log",
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
)
# Only record the levels ERROR or above
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Adding handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)


def get_prefixes(bot: commands.Bot, message: discord.Message) -> Union[str, List[str]]:
    """Returns prefixes from `data/config.json`."""
    data = config.load()

    if data["bot"].get("prefix") is None:
        return ">"

    else:
        return data["bot"]["prefix"]


# Constructing SnapBot object using commands.Bot class
class SnapBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=get_prefixes,  # Allows dynamic prefixes( prefix can change at runtime )
            intents=discord.Intents.all(),
            help_command=None,  # Disable the default help command
            strip_after_prefix=True,  # Strip any whitespaces when invoking a command
            case_insensitive=True,
        )

    async def load_extensions(self) -> None:
        """Loads extensions to the bot."""

        for file in os.listdir("snapbot/core/cogs"):
            if file in ["__pycache__", "__init__.py"]:
                continue

            else:
                # file[:-3] = filename without .py extension
                await self.load_extension(f"cogs.{file[:-3]}")

    async def setup_hook(self) -> None:
        """Used for syncing application commands with discord and for storing persistent views."""
        await self.tree.sync()

    async def on_ready(self) -> None:
        """This function is called when the bot's internal cache is ready."""
        print(f"\nLogged in as {self.user}")
        logger.info(f"Logging in as {self.user}")


bot = SnapBot()


async def main() -> None:
    """The main entrypoint function for starting the bot using the token."""
    await bot.load_extensions()
    await bot.start(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    
    # To prevent flooding of errors in the console when using Ctrl + C for stopping the bot
    except KeyboardInterrupt:
        print("\nShutting down...\n")
