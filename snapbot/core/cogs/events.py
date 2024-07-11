import discord
from discord.ext import commands

from shared.handlers import load_database

coll = load_database("afk")


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    async def welcome_back_user(self, message: discord.Message, user: discord.Member) -> None:
        """Sends a message for greeting the user back for coming back from the AFK status in the server."""
        afk_data: dict = await coll.find_one({"user_id": user.id})
        try:
            await message.author.edit(nick=afk_data["nickname"])
            
        except:
            pass
        
        finally:
            await coll.delete_one({"user_id": user.id})
            
            await message.reply(f"> Welcome back {user.mention}! You had gone on {discord.utils.format_dt(afk_data["timestamp"], "F")}\n\n**Reason:** {afk_data["reason"]}")
        
    async def inform_user(self, message: discord.Message, user: discord.Member) -> None:
        """Sends a message to the user who pinged an AFK user in the user."""
        afk_data: dict = await coll.find_one({"user_id": user.id})
        await message.reply(f"**{user.display_name}** went AFK {discord.utils.format_dt(afk_data["timestamp"], 'R')}\n\n**Reason:** {afk_data["reason"]}")
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.user == message.author:
            return
        
        if await coll.find_one({"user_id": message.author.id}) is not None:
            await self.welcome_back_user(message, message.author)
            
        for user in message.mentions:
            if await coll.find_one({"user_id": user.id}) is not None:
                await self.inform_user(message, user)
                
            else:
                continue
            

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
            
        
        