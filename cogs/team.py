import discord
from discord import app_commands
from discord.ext import commands


class Team(commands.Cog, name="team"):
    """Team related commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="team", description="Team related commands")

    @group.command(name="create", description="Creates a new team")
    @app_commands.describe(name="The name of the team")
    async def team_create(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(f"[DEBUG] Created team with name \"{name}\"")


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
