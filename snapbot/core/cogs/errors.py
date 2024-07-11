from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

from shared.emojis import ERROR


class ExceptionManager(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def generate_and_send_error_embed(
        self, ctx: commands.Context, error: Union[str, commands.CommandError]
    ) -> discord.Embed:
        """Generates and sends a discord embed which displays the error provided which can be either a custom message string or an inherited part of `commands.CommandError` Exception."""
        error_embed = discord.Embed(
            description=error, color=discord.Color.random(), timestamp=datetime.now()
        )
        error_embed.set_footer(text="Contact the bot developer for more info!")

        await ctx.send(embed=error_embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.BadColourArgument):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Invalid Color Input\n\nIt looks like you've entered an invalid color. Please make sure to use a recognised color name or a valid hex code. Examples of valid color inputs include:\n\n- Color names: `red`, `blue`, `green`\n- Hex Codes: `#FF5733`, `#3498DB`, `#2ECC71`",
            )

        elif isinstance(error, commands.RoleNotFound):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Role Not Found\n\nIt seems like the specified role could not be found. Please make sure the role name is spelled correctly and exists in the server. For example:\n\n- Verify that the role name matches exactly, including any special characters or capitalization.",
            )

        elif isinstance(error, commands.MemberNotFound):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Member Not Found\n\nIt looks like the specified member could not be found. Please ensure the member's name or ID is correct and that they are part of the server. For example:\n\n- Verify that the member's username or ID is typed correctly.\n- Check if the member is currently in the server.",
            )

        elif isinstance(error, commands.UserNotFound):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} User Not Found\n\nIt seems like the specified user could not be found. Please ensure the username or ID is correct and try again. For example:\n\n- Verify that the username or ID is typed correctly.\n- Check if the user exists and is accessible.",
            )

        elif isinstance(error, commands.ChannelNotFound):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Channel Not Found\n\nIt seems like the spcified channel could not be found. Please ensure the channel's name or ID is correct and try again. For example:\n\n- Verify that the channel is a text channel.\n- Check if the text channel exists and is accessible.",
            )

        elif isinstance(error, commands.BadArgument):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Invalid Input\n\nIt looks like one or more inputs you provided are invalid. Please ensure that all inputs are correct and try again. For example:\n\n- Ensure numeric inputs are valid numbers.\n- Check that text inputs match the expected format.",
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Missing Required Input\n\nIt seems like you've missed a required input. Please ensure you provide all necessary inputs. For example:\n\n - For this command: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
            )

        elif isinstance(error, commands.CommandOnCooldown):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Command On Cooldown\n\nThis command is currently on cooldown. Please wait a few moments before trying again. Cooldown time remaining: `{error.retry_after: .2f} seconds`.",
            )

        elif isinstance(error, commands.NoPrivateMessage):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Command Not Available in Private Messages\n\nThis command cannot be used in private messages. Please use this command in a server channel instead.",
            )

        elif isinstance(error, commands.MissingPermissions):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Insufficient Permissions\n\nYou do not have sufficient permissions to execute this command.",
            )

        elif isinstance(error, commands.BotMissingPermissions):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Bot Missing Permissions\n\nI do not have sufficient permissions to execute this command. Please ensure I have the necessary permissions and try again.",
            )

        elif isinstance(error, commands.MissingRole):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Missing Required Role\n\nYou need a specific role to execute this command.",
            )

        elif isinstance(error, commands.BotMissingRole):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Bot Missing Required Role\n\nI need a specific role to execute this command.",
            )

        elif isinstance(error, commands.MissingAnyRole):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Missing Required Role\n\nYou need at least one of the required roles to execute this command.",
            )

        elif isinstance(error, commands.BotMissingAnyRole):
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Bot Missing Required Role\n\nI need at least one of the required roles to execute this command.",
            )

        elif isinstance(error, commands.CommandNotFound):
            return  # Do not send anything if the command is not found

        else:
            await self.generate_and_send_error_embed(
                ctx,
                error=f"### {ERROR} Something Went Wrong\n\nAn unexpected error occurred while processing your request. Please try again later.",
            )

            # Raise the unknown/uncaught error that occurred so the library logger can log it
            # Debugging the error later will be easier this way
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExceptionManager(bot))
