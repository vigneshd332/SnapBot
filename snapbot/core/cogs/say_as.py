from typing import Union

import discord
from discord import app_commands as app
from discord.ext import commands

from shared.handlers import ConfigLoader
from shared.emojis import SUCCESS

config = ConfigLoader()

class SayAs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    async def fetch_webhook(self, channel: Union[discord.TextChannel, discord.VoiceChannel]) -> discord.Webhook:
        """Returns a webhook for the specified channel. If it's not present, it will make one."""
        
        webhooks = await channel.webhooks()
        if not webhooks or discord.utils.get(webhooks, name="SnapBot") is None:
            webhook = await channel.create_webhook(name="SnapBot")
            return webhook
        
        webhook = discord.utils.get(webhooks, name="SnapBot")
        return webhook
        
    @commands.hybrid_command(
        name="say_as",
        description="Mimic other user's and say anything!",
        aliases=["mimic"]
    )
    @app.describe(user="The member to imitate", message="The message to say")
    @commands.cooldown(1, 10)
    async def say_as(self, ctx: commands.Context, user: discord.Member, *, message: str) -> None:
        data = config.load()
        log_channel = ctx.guild.get_channel(data["channels"]["logs"])
        
        # Fetch the webhook, or create it if needed
        webhook = await self.fetch_webhook(ctx.channel)
        
        # Send the webhook
        await webhook.send(
            message,
            username=user.display_name,
            avatar_url=user.display_avatar.url
        )
        
        # If the command was invoked using slash
        if ctx.interaction:
            await ctx.reply(f"{SUCCESS} Done!", ephemeral=True)
        
        # If the command was invoked using a prefix( a normal prefix command )
        else:
            await ctx.message.delete()
            
        if log_channel is not None:
            await log_channel.send(f"{ctx.author.id} said **{message}**")
            

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SayAs(bot))