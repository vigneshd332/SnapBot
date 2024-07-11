from datetime import datetime
import discord
from discord import app_commands as app
from discord.ext import commands

from shared.handlers import load_database
from shared.emojis import INFO

coll = load_database("afk")


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    def generate_afk_embed(self, ctx: commands.Context, reason: str) -> discord.Embed:
        """Returns a discord embed which displays the details when the user went AFK."""
        afk_embed = discord.Embed(
            description=f"**{ctx.author.display_name}** went AFK {discord.utils.format_dt(datetime.now(), "R")}\n\n{INFO} Reason: **{reason}**",
            color=discord.Color.random(),
            timestamp=datetime.now()
        ).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url).set_thumbnail(url=ctx.author.display_avatar.url)
        
        return afk_embed
               
    @commands.hybrid_command(name="afk", description="Sets your status to AFK in the server!")
    @app.describe(reason="Why are you going AFK?")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def afk(self, ctx: commands.Context, *, reason: commands.Range[str, None, 500] = "Not Provided") -> None:
        afk_data = await coll.find_one({"user_id": ctx.author.id})
        
        # It means the user wasn't afk before they ran this command
        if afk_data is None:
            await coll.insert_one({
                "user_id": ctx.author.id,
                "reason": reason,
                "timestamp": datetime.now(),
                "nickname": ctx.author.nick
            })
            try:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            
            except discord.Forbidden:
                pass
                
            finally:
                await ctx.send(embed=self.generate_afk_embed(ctx, reason))
        
        # It means the user was already AFK before they ran this command
        else:
            await coll.delete_one({"user_id": ctx.author.id})
            try:
                await ctx.author.edit(nick=afk_data["nickname"])
                
            except discord.Forbidden:
                pass
            
            finally:
                await ctx.reply(f"> Welcome back {ctx.author.mention}! You had gone on {discord.utils.format_dt(afk_data["timestamp"], "F")}\n\n**Reason:** {afk_data["reason"]}")
                

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AFK(bot))
            