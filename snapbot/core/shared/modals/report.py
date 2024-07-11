from datetime import datetime
import discord

from shared.handlers import load_database, ConfigLoader
from shared.emojis import SUCCESS, INFO

coll = load_database("user_reports")
config = ConfigLoader()


class ReportModal(discord.ui.Modal):
    def __init__(self, reported_user: discord.Member) -> None:
        super().__init__(title="User Behaviour Report Form")
        self.reported_user = reported_user

    report_reason = discord.ui.TextInput(
        label="Reason for Report",
        placeholder="Eg: Harassment, Spam, e.t.c...",
        style=discord.TextStyle.short,
        max_length=1024,
    )
    description = discord.ui.TextInput(
        label="Violation Description",
        placeholder="Describe the issue in detail...",
        style=discord.TextStyle.paragraph,
        max_length=1024,
    )
    date_and_time = discord.ui.TextInput(
        label="Date and Time of Incident",
        placeholder="Enter when the incident occurred...",
        style=discord.TextStyle.short,
        max_length=1024,
    )
    comments = discord.ui.TextInput(
        label="Additional Comments",
        placeholder="Any extra information or comments( optional )",
        style=discord.TextStyle.long,
        max_length=1024,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        data = config.load()  # Load data from config.toml

        # Insert the collection into the database
        await coll.insert_one(
            {
                "submitted_by": interaction.user.id,
                "reported_user": self.reported_user.id,
                "reason": self.report_reason.value,
                "incident_datetime": self.date_and_time.value,
                "submitted_at": datetime.now(),
                "add_comments": self.comments.value,
            }
        )

        # Count all the docs in the database collection for display purposes
        count = await coll.count_documents({})

        # Create the embed which will display the report form details in the user reports channel
        report_embed = discord.Embed(
            title=f"User Report #{count}",
            color=discord.Color.random(),
            timestamp=datetime.now(),
        ).set_thumbnail(url=interaction.guild.icon.url)

        report_embed.add_field(
            name="Reported By:", value=interaction.user.mention, inline=False
        )
        report_embed.add_field(
            name="Reported User:", value=self.reported_user.mention, inline=False
        )
        report_embed.add_field(
            name="Reason for Report:", value=self.report_reason.value, inline=False
        )
        report_embed.add_field(
            name="Violation Description:", value=self.description.value, inline=False
        )
        report_embed.add_field(
            name="Date & Time of Incident:",
            value=self.date_and_time.value,
            inline=False,
        )
        report_embed.add_field(
            name="Additional Comments:", value=self.comments.value, inline=False
        )

        # Get the user reports channel and send the embed in that channel
        report_channel = interaction.guild.get_channel(data["channels"]["user_reports"])
        await report_channel.send(embed=report_embed)

        await interaction.followup.send(
            f"# {SUCCESS} Report Submission Confirmation\n\n**Thank you for our report!**\n\nWe have receieved your submission and will review it as soon as possible. If additional information is required, a staff member may contact you. Please note that due to the volume of reports, response times may vary.\n\n{INFO} If you have any further evidence or updates, please reach out to the staff team."
        )
