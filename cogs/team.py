import discord
from discord import app_commands
from discord.ext import commands

from models import Team


class TeamCog(commands.Cog, name="team"):
    """Team related commands."""

    NO_TEAM: str = ""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.teams: dict[str, Team] = dict()    # team_name -> Team
        self.players: dict[int, Team] = dict()  # player_id -> Team

    @app_commands.command(name="teams", description="Lists all the existing teams")
    async def teams(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Teams:\n" + "\n".join([team.name for team in self.teams.values()])
        )

    group = app_commands.Group(name="team", description="Team related commands")

    @group.command(name="create", description="Creates a new team")
    @app_commands.describe(name="The name of the team")
    async def team_create(self, interaction: discord.Interaction, name: str):
        player: discord.Member = interaction.user

        # check if player is already in a team
        current_team = self.players.get(player.id, TeamCog.NO_TEAM)
        if current_team != TeamCog.NO_TEAM:
            await interaction.response.send_message(
                f"You are already in a team! Please leave your current team first: \"{current_team.name}\".",
                ephemeral=True
            )
            return

        # check if a team with the given name already exists
        if name in self.teams:
            await interaction.response.send_message(
                f"A team with the name \"{name}\" already exits! Please choose a different name.",
                ephemeral=True
            )
            return

        new_team: Team = Team(name=name, owner_id=player.id)

        self.teams[name] = new_team
        self.players[player.id] = new_team

        await interaction.response.send_message(f"Team \"{name}\" was successfully created!", ephemeral=True)

    @group.command(name="disband", description="Disbands/deletes your team")
    async def team_disband(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"[DEBUG] disbanding...", ephemeral=True)

    @group.command(name="transfer_ownership", description="Transfers your team's ownership to another player")
    @app_commands.describe(player="The player to transfer the ownership to")
    async def team_transfer_ownership(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(
            f"[DEBUG] Transferred ownership to \"{player.display_name}\"", ephemeral=True
        )

    @group.command(name="invite", description="Invites a player to your team")
    @app_commands.describe(player="The player to invite")
    async def team_invite(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(f"[DEBUG] Invited \"{player.display_name}\"", ephemeral=True)

    @group.command(name="remove", description="Removes a player from your team")
    @app_commands.describe(player="The player to remove")
    async def team_remove(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(f"[DEBUG] Removed \"{player.display_name}\"", ephemeral=True)

    @group.command(name="list", description="Lists the players on your team")
    async def team_list(self, interaction: discord.Interaction):
        player: discord.Member = interaction.user

        # check if player is not in a team
        current_team: Team | TeamCog.NO_TEAM = self.players.get(player.id, TeamCog.NO_TEAM)
        if current_team == TeamCog.NO_TEAM:
            await interaction.response.send_message("You are not in a team!", ephemeral=True)
            return

        team_players: list[discord.Member] = []
        for player_id in current_team.players:
            player: discord.Member | None = interaction.guild.get_member(player_id)
            if player is not None:
                team_players.append(player)

        await interaction.response.send_message(
            f"\"{current_team.name}\" players:\n"
            "\n".join([player.display_name for player in team_players]),
            ephemeral=True
        )

    @group.command(name="points", description="Displays your team's points")
    async def team_points(self, interaction: discord.Interaction):
        player: discord.Member = interaction.user

        # check if player is not in a team
        current_team = self.players.get(player.id, TeamCog.NO_TEAM)
        if current_team == TeamCog.NO_TEAM:
            await interaction.response.send_message("You are not in a team!", ephemeral=True)
            return

        await interaction.response.send_message(
            f"\"{current_team.name}\" has {current_team.points} points", ephemeral=True
        )

    @group.command(name="leave", description="Leaves your current team")
    async def team_leave(self, interaction: discord.Interaction):
        player: discord.Member = interaction.user

        # check if player is not in a team
        current_team = self.players.get(player.id, TeamCog.NO_TEAM)
        if current_team == TeamCog.NO_TEAM:
            await interaction.response.send_message("You are not in a team!", ephemeral=True)
            return

        current_team.remove_player(player.id)
        self.players.pop(player.id)

        await interaction.response.send_message(f"Successfully left team \"{current_team.name}\"", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCog(bot))
