from datetime import datetime
from typing import List, Optional, Union

import discord
from discord import app_commands as app
from discord.ext import commands


class Avatar(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="avatar",
        description="Displays the specified user's discord avatar!",
        aliases=["av", "pfp", "dp"],
    )
    @app.describe(user="Whose avatar do you want to view?")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def avatar(
        self,
        ctx: commands.Context,
        *,
        user: Optional[Union[discord.Member, discord.User]],
    ) -> None:
        # If the user parameter is not provided by the user
        if user is None:
            user = ctx.author

        await ctx.defer()  # Defer the response

        embeds: List[discord.Embed] = []  # Store avatar embeds here

        # If the user's global avatar is not None
        if user.avatar is not None:
            embeds.append(
                discord.Embed(
                    title=f"{user.display_name}'s Global Avatar!",
                    color=discord.Color.random(),
                    timestamp=datetime.now(),
                )
                .set_author(
                    name=f"Requested by {ctx.author.display_name}!",
                    icon_url=ctx.author.display_avatar.url,
                )
                .set_image(url=user.avatar.url)
            )

        # If the user is a discord.Member and has a guild specific avatar
        if isinstance(user, discord.Member) and user.guild_avatar is not None:
            embeds.append(
                discord.Embed(
                    title=f"{user.display_name}'s Guild Avatar!",
                    color=discord.Color.random(),
                    timestamp=datetime.now(),
                )
                .set_author(
                    name=f"Requested by {ctx.author.display_name}!",
                    icon_url=ctx.author.display_avatar.url,
                )
                .set_image(url=user.guild_avatar.url)
            )

        # If the user neither has a global avatar nor a guild specific avatar
        # NOTE: This is important because accessing the url of 'None' properties will raise an error
        # In this case, the attribute 'display_avatar' will be used for displaying the default discord avatar
        if (
            user.avatar is None
            and isinstance(user, discord.Member)
            and user.guild_avatar is None
        ):
            embeds.append(
                discord.Embed(
                    title=f"{user.display_name}'s Avatar!",
                    color=discord.Color.random(),
                    timestamp=datetime.now(),
                )
                .set_author(
                    name=f"Requested by {ctx.author.display_name}!",
                    icon_url=ctx.author.display_avatar.url,
                )
                .set_image(url=user.display_avatar.url)
            )

        await ctx.send(embeds=embeds)  # Send the embeds


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Avatar(bot))
