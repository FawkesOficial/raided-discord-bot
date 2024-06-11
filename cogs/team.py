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

    @group.command(name="disband", description="Disbands/deletes your team")
    async def team_disband(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"[DEBUG] disbanding...")

    @group.command(name="transfer_ownership", description="Transfers your team's ownership to another player")
    @app_commands.describe(player="The player to transfer the ownership to")
    async def team_transfer_ownership(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(f"[DEBUG] Transferred ownership to \"{player.name}\"")

    @group.command(name="invite", description="Invites a player to your team")
    @app_commands.describe(player="The player to invite")
    async def team_invite(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(f"[DEBUG] Invited \"{player.name}\"")

    @group.command(name="remove", description="Removes a player from your team")
    @app_commands.describe(player="The player to remove")
    async def team_remove(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(f"[DEBUG] Removed \"{player.name}\"")

    @group.command(name="list", description="Lists the players on your team")
    async def team_list(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"[DEBUG] players...")

    @group.command(name="score", description="Displays your team's score")
    async def team_score(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"[DEBUG] score: 1000")


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
