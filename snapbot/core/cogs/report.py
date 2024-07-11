import discord
from discord import app_commands as app
from discord.ext import commands

from shared.modals import ReportModal


class Report(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app.command(
        name="report_user",
        description="Reports the specified member of the server to the staff members!",
    )
    @app.describe(user="Who are you reporting?")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def report_user(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        await interaction.response.send_modal(ReportModal(user))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Report(bot))
