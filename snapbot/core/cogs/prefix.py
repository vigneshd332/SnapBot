import json
from typing import Dict, List, Union

from discord.ext import commands

from shared.handlers import ConfigLoader
from shared.emojis import DENIED, INFO, SUCCESS

config = ConfigLoader()
data = config.load()  # Load data from config.toml


class Prefix(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="set_prefix",
        description="Changes the prefix of the bot",
        aliases=["change_prefix"],
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def set_prefix(self, ctx: commands.Context, prefix: str) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()

        data["bot"]["prefix"] = prefix
        config.save(data)  # Save the changes

        await ctx.reply(f"{SUCCESS} Prefix successfully changed to **{prefix}**")

    @commands.hybrid_command(
        name="add_prefix", description="Adds the provided prefix to the bot"
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def add_prefix(self, ctx: commands.Context, prefix: str) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()

        # If the prefix is just a string, make it a list
        if isinstance(data["bot"]["prefix"], str):
            data["bot"]["prefix"] = [data["bot"]["prefix"], prefix]
            config.save(data)  # Save the changes

        # If the prefix is already in the list format, append to the list
        else:
            data["bot"]["prefix"].append(prefix)
            config.save(data)

        await ctx.reply(f"{SUCCESS} Prefix **{prefix}** added successfully!")

    @commands.hybrid_command(
        name="delete_prefix",
        description="Deletes/Removes a prefix from the bot",
        aliases=["remove_prefix"],
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delete_prefix(self, ctx: commands.Context, prefix: str) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()

        # If there's only one prefix left, don't remove it
        if isinstance(data["bot"]["prefix"], str) or data["bot"]["prefix"] == prefix:
            await ctx.reply(f"{DENIED} Can't remove the only available prefix!")
            return

        # Try removing the prefix
        try:
            data["bot"]["prefix"].remove(prefix)

        # If the prefix is not found
        except:
            await ctx.reply(f"{DENIED} Prefix not found!")

        else:
            config.save(data)
            await ctx.reply(f"{SUCCESS} **{prefix}** removed successfully!")

    @commands.hybrid_command(
        name="list_prefix",
        description="Lists all the current prefixes the bot has",
        aliases=["show_prefix"],
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def list_prefix(self, ctx: commands.Context) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()

        # If the prefix is only just a string
        if isinstance(data["bot"]["prefix"], str):
            await ctx.reply(f"{INFO} The current prefix is **{data["bot"]["prefix"]}**")
            return

        # If the prefix is a list, iterate over each prefix and show it to the user
        content = ""
        for index, prefix in enumerate(data["bot"]["prefix"], start=1):
            content += f"{index}. **{prefix}**\n"

        await ctx.reply(content)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Prefix(bot))
