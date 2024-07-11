from datetime import datetime
from typing import List

import discord
from discord import app_commands as app
from discord.ext import commands

from shared.emojis import INFO, PURPLE_ARROW, STAR, DENIED, SUCCESS
from shared.handlers import ConfigLoader

config = ConfigLoader()
data = config.load()


class Colors(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def generate_color_roles_embed(
        self, ctx: commands.Context, color_roles: List[discord.Role]
    ) -> discord.Embed:
        """Generates a discord embed which displays the available color roles that the users can pick using the `get_color` command."""

        embed = discord.Embed(
            title="List of Available Color Roles!",
            description=f"{STAR} To get a color role, use the `{ctx.prefix}get_color <color_role_name>` command!\n\n",
            color=discord.Color.random(),
            timestamp=datetime.now(),
        )
        # Iterate over each role and format it
        for role in color_roles:
            embed.description += f"{PURPLE_ARROW} {role.mention}\n\n"

        return embed

    @commands.hybrid_command(
        name="create_color_role",
        description="Creates a color role in the server!",
        aliases=["create_colour_role"],
    )
    @app.describe(
        color="Enter the hex code of the color", name="Enter the name of the color role"
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_any_role(*data["roles"]["staff_roles"])
    async def create_color_role(
        self, ctx: commands.Context, color: commands.ColorConverter, *, name: str
    ) -> None:
        await ctx.defer(ephemeral=True)  # Defer the response
        data = config.load()  # Load data from config.toml

        # If a role already exists with the name or color provided by the user
        if (
            discord.utils.find(
                lambda role: role.name.lower() == name.lower() or role.color == color,
                ctx.guild.roles,
            )
            is not None
        ):
            await ctx.reply(
                f"{DENIED} A role already exists with the specified color or name!"
            )
            return

        # Create the role in the server
        role = await ctx.guild.create_role(
            reason=f"Created a color role with the name {name} by {ctx.author.name}",
            name=name,
            color=color,
        )

        # Grab all the color roles from the server and store them in a list
        color_roles = [
            role
            for role in ctx.guild.roles
            if role.color.value != 0
            and not role.permissions.value
            and role.name not in data["roles"]["excluded_color_roles"]
        ]

        # Get the channel where the color roles list is supposed to be
        color_roles_channel = ctx.guild.get_channel(
            data["channels"]["color_roles_list"]
        )

        # If the channel is not found
        if color_roles_channel is None:
            await ctx.reply(
                f"{INFO} {role.mention} created successfully without updating the color roles list!"
            )
            return

        # Get the message from the provided channel which is sent by snapbot, has no content but only an embed
        message = await discord.utils.find(
            lambda m: m.author == self.bot.user
            and not m.content
            and m.embeds
            and m.embeds[0].title == "List of Available Color Roles!",
            color_roles_channel.history(),
        )

        # If the message is not found or if it doesn't exist
        if message is None:
            await ctx.reply(
                f"{INFO} {role.mention} created successfully without updating the color roles list!"
            )
            return

        # If the message exists, update the embed of that message which we just retrieved
        embed = self.generate_color_roles_embed(ctx, color_roles)
        await message.edit(embed=embed)
        await ctx.reply(f"{SUCCESS} {role.mention} created successfully!")

    @commands.hybrid_command(
        name="display_color_roles",
        description="Sends a list displaying all the color roles present in the server!",
        aliases=["send_color_roles"],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_any_role(*data["roles"]["staff_roles"])
    async def display_color_roles(self, ctx: commands.Context) -> None:
        await ctx.defer()  # Defer the response
        data = config.load()  # Load data from config.toml

        # Grab all the color roles from the server and store them in a list
        color_roles = [
            role
            for role in ctx.guild.roles
            if role.color.value != 0
            and not role.permissions.value
            and role.name not in data["roles"]["excluded_color_roles"]
        ]
        # If the list is empty, means no color roles
        if color_roles == []:
            await ctx.reply(f"{DENIED} No color roles found!")

        # Create an embed which will display all the color roles available for use
        embed = self.generate_color_roles_embed(ctx, color_roles)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="get_color",
        description="Use this command to get a color role for yourself!",
        aliases=["get_colour", "get_color_role", "get_colour_role"],
    )
    @app.describe(name="Enter the name of color role")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def get_color(self, ctx: commands.Context, *, name: str) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()  # Load data from config.toml

        # Try finding the color role the user wants
        color_role = discord.utils.find(
            lambda role: role.name.lower().replace(" ", "")
            == name.lower().strip().replace(" ", "")
            and not role.permissions.value
            and role.color.value != 0
            and role.name not in data["roles"]["excluded_color_roles"],
            ctx.guild.roles,
        )
        # If the color role is not present
        if color_role is None:
            await ctx.reply(f"{DENIED} No color role found with the name **{name}**.")
            return

        # Iterate over each role the author has and remove any existing color roles
        for role in ctx.author.roles:
            # If the role is a color role, remove it
            if role.name in [
                r.name
                for r in ctx.guild.roles
                if not r.permissions.value and r.color.value != 0
            ]:
                await ctx.author.remove_roles(role)

            # If the role is not a color role, continue
            else:
                continue

        await ctx.author.add_roles(color_role)
        await ctx.reply(
            f"{SUCCESS} Successfully added **{color_role.name}** to your profile!"
        )

    @commands.hybrid_command(
        name="set_color_roles_list_channel",
        description="Sets the specified channel for displaying the color roles list!",
        aliases=["set_colour_roles_list_channel"],
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def set_color_roles_list_channel(
        self, ctx: commands.Context, *, channel: commands.TextChannelConverter
    ) -> None:
        # Load data from config.toml and set the specified color roles list channel's id
        data = config.load()
        data["channels"]["color_roles_list"] = channel.id
        config.save(data)  # Save the changes

        await ctx.reply(
            f"{SUCCESS} Color roles list channel successfully set to {channel.mention}!"
        )

    @commands.hybrid_command(
        name="exclude_color_role",
        description="Excludes the specified color role from the list!",
        aliases=["exclude_colour_role"],
    )
    @commands.has_any_role(*data["roles"]["staff_roles"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def exclude_color_role(
        self, ctx: commands.Context, *, role: commands.RoleConverter
    ) -> None:
        # If the role specified by the user is not a color role
        if discord.utils.find(lambda r: r.color == role.color, ctx.guild.roles) is None:
            await ctx.reply(f"{DENIED} Not a valid color role!", ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        data = config.load()  # Load data from config.toml

        # If the color role is already in the excluded list, remove it
        if role.name in data["roles"]["excluded_color_roles"]:
            data["roles"]["excluded_color_roles"].remove(role.name)
            config.save(data)  # Save the changes

            await ctx.reply(
                f"{SUCCESS} **{role.name}** removed from the excluded color roles list successfully! Update the color roles list manually by running `{ctx.prefix}display_color_role`!"
            )
            return

        # Add the role's name to the excluded list and save the changes
        data["roles"]["excluded_color_roles"].append(role.name)
        config.save(data)

        # Refresh the data by loading it again
        data = config.load()

        # Grab all the color roles from the server and store them in a list
        color_roles = [
            role
            for role in ctx.guild.roles
            if role.color.value != 0
            and not role.permissions.value
            and role.name not in data["roles"]["excluded_color_roles"]
        ]

        # Get the channel where the color roles list is supposed to be
        color_roles_channel = ctx.guild.get_channel(
            data["channels"]["color_roles_list"]
        )

        # If the channel is not found
        if color_roles_channel is None:
            await ctx.reply(
                f"{INFO} **{role.name}** successfully added to the excluded color roles list without updating the color roles list!"
            )
            return

        # Get the message from the provided channel which is sent by snapbot, has no content but only an embed
        message = await discord.utils.find(
            lambda m: m.author == self.bot.user
            and not m.content
            and m.embeds
            and m.embeds[0].title == "List of Available Color Roles!",
            color_roles_channel.history(),
        )

        # If the message is not found or if it doesn't exist
        if message is None:
            await ctx.reply(
                f"{INFO} **{role.name}** successfully added to the excluded color roles list without updating the color roles list!"
            )
            return

        # If the message exists, update the embed of that message which we just retrieved
        embed = self.generate_color_roles_embed(ctx, color_roles)
        await message.edit(embed=embed)
        await ctx.reply(
            f"{SUCCESS} **{role.name}** successfully added to the excluded color roles list!"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Colors(bot))
