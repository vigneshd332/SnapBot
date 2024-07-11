from datetime import datetime

import discord
from discord import app_commands as app
from discord.ext import commands

from shared.handlers import load_database, encrypt, decrypt, ConfigLoader
from shared.emojis import SUCCESS, DENIED, INFO

coll = load_database("confessions")
config = ConfigLoader()
data = config.load()


class Confession(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="confess",
        description="Posts an anonymous confession in the confessions channel!",
    )
    @app.describe(confession="What do you wanna confess?")
    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.guild_only()
    async def confess(
        self, ctx: commands.Context, *, confession: commands.Range[str, None, 2000]
    ) -> None:
        await ctx.defer(ephemeral=True)
        data = config.load()  # Load data from config.toml

        # Insert the confession in the database collection
        await coll.insert_one({"confession": confession})

        # NOTE: We don't have the previous records of the confessions so we are assuming the confession number count will start from around 76( approx. )
        count = await coll.count_documents({}) + 76

        # Create the embed which will display the confession in the confessions channel
        confession_embed = discord.Embed(
            description=confession,
            color=discord.Color.random(),
            timestamp=datetime.now(),
        ).set_author(name=f"Anonymous Confession #{count}")

        # Encrypt the author's user id
        encrypted_id = encrypt(str(ctx.author.id))

        # Create the log embed which will display the encrypted user id in the logs channel
        confession_log_embed = (
            discord.Embed(
                description=confession,
                color=discord.Color.random(),
                timestamp=datetime.now(),
            )
            .set_author(name="Confession logs successfully generated!")
            .add_field(name="Encrypted ID:", value=encrypted_id, inline=False)
        )

        # Get the logs and confession channel
        log_channel = ctx.guild.get_channel(data["channels"]["logs"])
        confession_channel = ctx.guild.get_channel(data["channels"]["confessions"])

        # Send the embeds to their respective channels
        await log_channel.send(embed=confession_log_embed)
        await confession_channel.send(embed=confession_embed)

        await ctx.reply(
            f"{SUCCESS} Your confession has been successfully posted in {confession_channel.mention}!"
        )

    @commands.hybrid_command(
        name="decrypt_confession",
        description="Decrypts the provided encrypted ID into the User ID",
    )
    @commands.guild_only()
    @commands.has_any_role(*data["roles"]["staff_roles"])
    async def decrypt_confession(
        self, ctx: commands.Context, encrypted_user_id: str
    ) -> None:
        # Try decrypting the user id
        decrypted_user_id = decrypt(encrypted_user_id)

        # If it returns None, it means the decryption process failed
        if decrypted_user_id is None:
            await ctx.reply(f"{DENIED} Invalid Encryption ID!", ephemeral=True)
            return

        await ctx.reply(
            f"{SUCCESS} Decrypted User ID: ``{decrypted_user_id}``", ephemeral=True
        )

        # Get the log channel and send a notification displaying who accessed the confession logs and at what time
        data = config.load()
        log_channel = ctx.guild.get_channel(data["channels"]["logs"])
        await log_channel.send(
            f"{INFO} {ctx.author.mention} accessed confession logs on {discord.utils.format_dt(datetime.now(), 'F')}"
        )


async def setup(bot: commands.Bot) -> None:
        await bot.add_cog(Confession(bot))
