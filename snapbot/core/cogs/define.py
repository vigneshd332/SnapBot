from datetime import datetime
from typing import Generator, List

import discord
from reactionmenu import ViewButton, ViewMenu
import requests
from discord import app_commands as app
from discord.ext import commands

from shared.emojis import DENIED


class Define(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def generate_definition_embeds(
        self, ctx: commands.Context, word: str, data: List[dict]
    ) -> Generator[discord.Embed, None, None]:
        """Generates varying amount of discord embeds where each embed display information for the specified word using the data fetched from the Urban Dictionary."""

        for entry in data:
            definition: str = entry["definition"]
            example: str = entry["example"]
            author: str = entry["author"]

            embed = (
                discord.Embed(
                    description=f"**{word}**: {definition}\n\n**Example**: {example}",
                    color=discord.Colour.random(),
                    timestamp=datetime.now(),
                )
                .set_author(
                    name=f"Requested By {ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url,
                )
                .set_footer(text=f"Written by {author}")
            )

            yield embed

    def generate_navigation_buttons(self) -> List[ViewButton]:
        """Generates buttons that will be used for navigation purposes in the define command."""

        next_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Next",
            custom_id=ViewButton.ID_NEXT_PAGE,
            emoji="➡️",
        )
        previous_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Previous",
            custom_id=ViewButton.ID_PREVIOUS_PAGE,
            emoji="⬅️",
        )
        go_to_first_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Go to First",
            custom_id=ViewButton.ID_GO_TO_FIRST_PAGE,
            emoji="⏮️",
        )
        go_to_last_button = ViewButton(
            style=discord.ButtonStyle.secondary,
            label="Go to Last",
            custom_id=ViewButton.ID_GO_TO_LAST_PAGE,
            emoji="⏭️",
        )

        return [go_to_first_button, previous_button, next_button, go_to_last_button]

    @commands.hybrid_command(
        name="define",
        description="Query Urban Dictionary for a word's definition and example.",
        aliases=["search", "def"],
    )
    @app.describe(word="What do you want to search?")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def define(self, ctx: commands.Context, word: str) -> None:
        # URL for making http request to Urban Dictionary
        url = f"https://api.urbandictionary.com/v0/define?term={word}"

        # Get the response using the url
        response = requests.get(url)

        # If the response status code is not 200( ERROR occurred )
        if response.status_code != 200:
            await ctx.reply(
                f"{DENIED} Urban Dictionary API is down! Please try again later.",
                ephemeral=True,
            )
            return

        # Convert the response data into a dict
        response_in_json: dict = response.json()

        # If the data doesn't contain any definitions or examples
        if not response_in_json["list"]:
            await ctx.reply(
                f"{DENIED} No definitions found for the word: **{word}**", ephemeral=True
            )
            return

        await ctx.defer()  # Defer the response

        # Get the data list from the response
        data: List[dict] = response_in_json["list"]

        embeds: list[discord.Embed] = []  # Store the embeds here

        # Add all the embeds generated from the function to the embeds list we defined above
        for embed in self.generate_definition_embeds(ctx, word=word, data=data):
            embeds.append(embed)

        # Create a view menu of type Embed
        view_menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed)

        # Add embeds list as pages to the view menu
        view_menu.add_pages(embeds)

        # Add buttons to the view menu
        buttons = self.generate_navigation_buttons()
        view_menu.add_buttons(buttons)

        # Start the view menu
        await view_menu.start(reply=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Define(bot))
