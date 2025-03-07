import json
import random
from typing import Optional, Collection, Iterable, Self
from dataclasses import dataclass, field

import discord
from discord import app_commands
from discord.ext import commands

import config

type Player = discord.Member


@dataclass(frozen=True)
class Team:
    """
    Represents a generic team of players.

    Attributes
    ========
    name - the team's name
    owner_id - the Discord ID of the team's owner
    guild_id - the Discord Guild's ID where the team was created
    players - the list of the team's players Discord IDs
    points - the number of points the team has
    """

    name: str
    owner_id: int
    guild_id: int
    players: list[int] = field(default_factory=list)
    points: int = 0

    def __post_init__(self):
        if self.owner_id not in self.players:
            self.players.append(self.owner_id)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(**data)

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the team

        :param player: the player to add to the team
        :raises PlayerAlreadyOnTheTeam: if the player is already on the team
        :raises CannotAddBotToTeam: if `player` is a bot
        """

        if player.id in self.players:
            raise PlayerAlreadyOnTheTeam(player, self)

        if player.bot:
            raise CannotAddBotToTeam

        self.players.append(player.id)

    def remove_player(self, player: Player) -> None:
        """
        Removes a player from the team

        :param player: the player to remove from the team
        :raises PlayerNotOnTheTeam: if the player is not on the team
        :raises CannotRemoveTeamOwner: if `player` is the team's owner
        """

        if player.id not in self.players:
            raise PlayerNotOnTheTeam(player, self)

        if player.id == self.owner_id:
            raise CannotRemoveTeamOwner

        self.players.remove(player.id)

    def transfer_ownership(self, new_owner: Player) -> None:
        """
        Transfers the team's ownership to a new player on the team

        :param new_owner: the player to transfer the ownership to
        :raises PlayerNotOnTheTeam: if `new_owner` is not on the team
        :raises PlayerAlreadyIsOwner: if `new_owner` already is the team's owner
        """

        if new_owner.id not in self.players:
            raise PlayerNotOnTheTeam(new_owner, self)

        if self.is_owned_by(new_owner):
            raise PlayerAlreadyIsOwner(new_owner, self)

        object.__setattr__(self, "owner_id", new_owner.id)

    def is_owned_by(self, player: Player) -> bool:
        """
        Checks if the team is owned by the given player

        :param player: the player to check
        :return: `True` if the player is the owner of the team, `False` otherwise
        """
        return self.owner_id == player.id


class PlayerAlreadyOnTheTeam(Exception):

    def __init__(self, player: Player, team: Team):
        super().__init__(f"player {player.display_name} is already on the team \"{team.name}\"")

        self.player = player
        self.team = team


class PlayerNotOnTheTeam(Exception):

    def __init__(self, player: Player, team: Team):
        super().__init__(f"player {player.display_name} is not on the team \"{team.name}\"")

        self.player = player
        self.team = team


class PlayerAlreadyIsOwner(Exception):

    def __init__(self, player: Player, team: Team):
        super().__init__(f"player {player.display_name} already is the owner of the team \"{team.name}\"")

        self.player = player
        self.team = team


class GuildNotFoundError(Exception):

    def __init__(self, guild_id: int):
        super().__init__(f"guild with id \"{guild_id}\" could not be found")

        self.guild_id = guild_id


class CannotAddBotToTeam(Exception):

    def __init__(self):
        super().__init__(f"cannot add a bot to a team")


class PlayerNotOnATeam(Exception):

    def __init__(self, player: Player):
        super().__init__(f"player {player.display_name} is not on a team")

        self.player = player


class PlayerNotTeamOwner(Exception):

    def __init__(self, player: Player, team: Team):
        super().__init__(f"player {player.display_name} is not the owner of \"{team.name}\"")

        self.player = player
        self.team = team


class CannotRemoveTeamOwner(Exception):

    def __init__(self):
        super().__init__(f"cannot remove the team's owner from the team")


class Replies:
    # Static messages
    no_teams_registered: str = "No teams registered."
    player_not_on_a_team: str = "You are not on a team!"
    player_not_team_owner: str = "You are not the team's owner!"
    player_already_is_owner: str = "You can't transfer the ownership to yourself!"
    trying_to_add_bot_to_team: str = "You cannot add a bot to your team!"
    cant_remove_owner_from_team: str = "You cannot remove the team's owner from the team!"

    # Dynamic messages
    @staticmethod
    def team_display(*, team: Team) -> str:
        return f"{team.name} - {len(team.players)} player(s)"

    @staticmethod
    def teams_display(*, teams: Iterable[Team]) -> str:
        return "Teams:\n" \
             + "\n".join(map(lambda team: Replies.team_display(team=team), teams))

    @staticmethod
    def already_on_a_team(*, current_team: Team) -> str:
        return f"You are already on a team! Please leave your current team first: \"{current_team.name}\"."

    @staticmethod
    def team_already_exists(*, team_name: str) -> str:
        return f"A team with the name \"{team_name}\" already exits! Please choose a different name."

    @staticmethod
    def team_created(*, created_team: Team) -> str:
        return f"Team \"{created_team.name}\" was successfully created!"

    @staticmethod
    def team_disbanded_notify_player(*, previous_team: Team, previous_owner: Player) -> str:
        return f"{previous_owner.display_name} disbanded/deleted the team you were on ({previous_team.name}).\n" \
              + "You no longer have a team!"

    @staticmethod
    def team_disbanded_successfully(*, disbanded_team: Team) -> str:
        return f"Successfully disbanded/deleted \"{disbanded_team.name}\".\n" \
             + "You no longer have a team!"

    @staticmethod
    def player_not_on_the_team(*, player: Player) -> str:
        return f"{player.mention} is not on your team.\n" \
              + "Please choose a player that is on your team.\n" \
              + "You can see the list of your team's player using `/team list`"

    @staticmethod
    def ownership_transferred_successfully(*, team: Team, new_owner: Player) -> str:
        return f"Successfully transferred ownership of \"{team.name}\" to {new_owner.mention}!"

    @staticmethod
    def team_points_display(*, team: Team) -> str:
        return f"\"{team.name}\" has {team.points} points."

    @staticmethod
    def team_player_display(*, player: Player) -> str:
        return player.display_name

    @staticmethod
    def team_players_list(*, team: Team, team_players: Iterable[Player]) -> str:
        return f"\"{team.name}\" players:\n" \
              + "\n".join(map(lambda player: Replies.team_player_display(player=player), team_players))

    @staticmethod
    def invited_player(*, player: Player) -> str:
        return f"Successfully invited {player.mention}\n" \
             + f"When {player.mention} replies to your invitation, you will get a DM with their response!"

    @staticmethod
    def player_already_on_the_team(*, player: Player, team: Team) -> str:
        return f"{player.mention} is already on \"{team.name}\"!"

    @staticmethod
    def team_player_removed_notify(*, team: Team) -> str:
        return f"You have been removed from \"{team.name}\" team!"

    @staticmethod
    def team_removed_player(*, team: Team, player: Player) -> str:
        return f"Successfully removed {player.mention} from \"{team.name}\"!"

    @staticmethod
    def team_player_promoted_to_owner_notify(*, team: Team, previous_owner: Player) -> str:
        return f"{previous_owner.display_name} left the team you are on ({team.name}).\n" \
              + "You are now the team's owner!"

    @staticmethod
    def player_left_team_successfully(*, team: Team) -> str:
        return f"Successfully left \"{team.name}\""

    @staticmethod
    def player_owner_transfer_notify(*, team: Team, previous_owner: Player) -> str:
        return f"{previous_owner.display_name} transferred the ownership of \"{team.name}\" to you.\n" \
              + "You are now the team's owner!"

    @staticmethod
    def no_registered_team_with_name(*, team_name: str) -> str:
        return f"There is no such team with name \"{team_name}\"!\n" \
              + "To see the list of registered teams, use the command `/teams`"


class TeamCog(commands.Cog, name="team"):
    """
    Team related commands.
    """

    group = app_commands.Group(name="team", description="Team related commands")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

        self._teams: dict[str, Team] = dict()                  # team_name -> Team
        self._player_id_to_team_name: dict[int, str] = dict()  # player_id -> team_name

        self.load_data()

    def load_data(self):
        try:
            with open(config.DATA_DIR / "teams.json", "r") as teams_file:
                data = json.load(teams_file)
                self._teams = {team_name: Team.from_dict(team_dict) for team_name, team_dict in data.items()}
        except FileNotFoundError:
            pass

        try:
            with open(config.DATA_DIR / "players.json", "r") as players_file:
                data = json.load(players_file)
                self._player_id_to_team_name = {int(player_id): team_name for player_id, team_name in data.items()}
        except FileNotFoundError:
            pass

    def save_data(self) -> None:
        with open(config.DATA_DIR / "teams.json", "w") as teams_file:
            json.dump(self._teams, teams_file, default=vars)

        with open(config.DATA_DIR / "players.json", "w") as players_file:
            json.dump(self._player_id_to_team_name, players_file, default=vars)

    # TODO: this does not need to be inside TeamCog specifically
    @staticmethod
    async def reply_to(interaction: discord.Interaction, message: str, hidden: bool = True):
        """
        Wrapper function around interaction.response.send_message()

        :param interaction: the interaction to reply to
        :param message: the reply's message
        :param hidden: whether the reply should be hidden
        """

        await interaction.response.send_message(message, ephemeral=hidden)

    @staticmethod
    async def notify(player: Player, message: str):
        """
        Wrapper function around discord.Member.send()
        Attempts to notify a player with a custom message

        :param player: the player to notify
        :param message: the notification's message
        """

        try:
            await player.send(message)
        except discord.Forbidden:
            # user doesn't allow messages from bots or private servers
            # TODO: add logging here informing that the user could not be messaged
            pass

    @property
    def teams_list(self) -> Collection[Team]:
        """
        Returns a collection of all registered teams

        :returns: a collection of all registered teams
        """

        return self._teams.values()

    def get_player_team(self, player: Player) -> Optional[Team]:
        """
        Returns the team the player belongs to, if the player belongs to one.

        :param player: the player whose team is going to be returned
        :returns: the player's team, if he belongs to one.
        """

        return self._teams.get(self._player_id_to_team_name.get(player.id))

    def get_team_players(self, team: Team) -> Collection[Player]:
        """
        Returns a collection of the players on a Team

        :param team: the team to get the players
        :return: a collection of the players on the Team
        :raises GuildNotFoundError: if the Discord Guild where the team was created could not be found
        """
        team_guild: Optional[discord.Guild] = self.bot.get_guild(team.guild_id)

        if team_guild is None:
            raise GuildNotFoundError(team.guild_id)

        return filter(lambda x: x is not None, map(team_guild.get_member, team.players))

    def get_team_owned_by_player(self, player: Player) -> Optional[Team]:
        """
        Wrapper around `self.get_player_team()`
        Returns given `player`s team if he belongs to one and owns it.

        :param player: the player whose team is going to be returned
        :returns: the player's team, if he owns it
        :raises PlayerNotOnATeam: if `player` does not belong to a team
        :raises PlayerNotTeamOwner: if `player` is not the team's owner
        """

        player_team: Optional[Team] = self.get_player_team(player)

        if player_team is None:
            raise PlayerNotOnATeam(player)

        if not player_team.is_owned_by(player):
            raise PlayerNotTeamOwner(player, player_team)

        return player_team

    #
    #  - [ Individual Commands ] -
    #
    @app_commands.command(name="teams", description="Lists all the existing teams")
    async def teams(self, interaction: discord.Interaction):
        teams: Collection[Team] = self.teams_list

        if len(teams) > 0:
            await self.reply_to(interaction, Replies.teams_display(teams=teams))
        else:
            await self.reply_to(interaction, Replies.no_teams_registered)

    #
    # - [ /team Commands ] -
    #
    @group.command(name="create", description="Creates a new team")
    @app_commands.describe(team_name="The name of the team")
    async def team_create(self, interaction: discord.Interaction, team_name: str):
        """
        Attempts to create a new team and add it to the "teams" database.
        """
        owner: Player = interaction.user

        current_team: Optional[Team] = self.get_player_team(owner)

        if current_team is not None:
            await self.reply_to(interaction, Replies.already_on_a_team(current_team=current_team))
            return

        if team_name in self._teams:
            await self.reply_to(interaction, Replies.team_already_exists(team_name=team_name))
            return

        new_team: Team = Team(name=team_name, owner_id=owner.id, guild_id=interaction.guild_id)

        self._teams[team_name] = new_team
        self._player_id_to_team_name[owner.id] = team_name

        self.save_data()

        await self.reply_to(interaction, Replies.team_created(created_team=new_team))

    @group.command(name="disband", description="Disbands/deletes your team")
    async def team_disband(self, interaction: discord.Interaction):
        """
        Attempts to disband a player's team and remove it from the "teams" database.
        """

        owner: Player = interaction.user

        try:
            owner_team: Team = self.get_team_owned_by_player(owner)
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
            return

        for team_player in self.get_team_players(owner_team):
            self._player_id_to_team_name.pop(team_player.id)

            if team_player.id == owner_team.owner_id:
                continue

            await self.notify(
                team_player,
                Replies.team_disbanded_notify_player(previous_team=owner_team, previous_owner=owner)
            )

        self._teams.pop(owner_team.name)

        self.save_data()

        await self.reply_to(interaction, Replies.team_disbanded_successfully(disbanded_team=owner_team))

    @group.command(name="transfer_ownership", description="Transfers your team's ownership to a player on your team")
    @app_commands.describe(new_owner="The player to transfer the ownership to")
    async def team_transfer_ownership(self, interaction: discord.Interaction, new_owner: discord.Member):
        """
        Attempts to transfer the ownership of `current_owner`'s team to `new_owner`
        """

        owner: Player = interaction.user

        try:
            owner_team: Team = self.get_team_owned_by_player(owner)
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
            return

        try:
            owner_team.transfer_ownership(new_owner)
        except PlayerNotOnTheTeam:
            await self.reply_to(interaction, Replies.player_not_on_the_team(player=new_owner))
            return
        except PlayerAlreadyIsOwner:
            await self.reply_to(interaction, Replies.player_already_is_owner)
            return

        await self.notify(new_owner, Replies.player_owner_transfer_notify(team=owner_team, previous_owner=owner))

        self.save_data()

        await self.reply_to(
            interaction, Replies.ownership_transferred_successfully(team=owner_team, new_owner=new_owner)
        )

    @group.command(name="invite", description="Invites a player to your team")
    @app_commands.describe(player="The player to invite")
    async def team_invite(self, interaction: discord.Interaction, player: discord.Member):
        """
        Attempts to invite `player` to `owner`s team
        """

        owner: Player = interaction.user

        try:
            owner_team: Team = self.get_team_owned_by_player(owner)
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
            return

        # TODO: DEBUG!!!! ADDING PLAYER WITHOUT PERMISSION FOR TESTING PURPOSES
        try:
            owner_team.add_player(player)
        except PlayerAlreadyOnTheTeam:
            await self.reply_to(interaction, Replies.player_already_on_the_team(player=player, team=owner_team))
            return
        except CannotAddBotToTeam:
            await self.reply_to(interaction, Replies.trying_to_add_bot_to_team)
            return

        self._player_id_to_team_name[player.id] = owner_team.name

        self.save_data()

        # TODO: send message to invitee, notifying them that they have been invited to a team
        # TODO: with buttons for "Accept" and "Reject"
        await self.reply_to(interaction, Replies.invited_player(player=player))

        # TODO: missing case where `player` is already on a team. in this case, they should still receive an invite
        # TODO: but be informed that they are already on a team

    @group.command(name="remove", description="Removes a player from your team")
    @app_commands.describe(player="The player to remove")
    async def team_remove(self, interaction: discord.Interaction, player: discord.Member):
        """
        Attempts to remove `player` from `owner`s team
        """

        owner: Player = interaction.user

        try:
            owner_team: Team = self.get_team_owned_by_player(owner)
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
            return

        try:
            owner_team.remove_player(player)
        except PlayerNotOnTheTeam:
            await self.reply_to(interaction, Replies.player_not_on_the_team(player=player))
            return
        except CannotRemoveTeamOwner:
            await self.reply_to(interaction, Replies.cant_remove_owner_from_team)
            return

        self._player_id_to_team_name.pop(player.id)

        await self.notify(player, Replies.team_player_removed_notify(team=owner_team))

        self.save_data()

        await self.reply_to(interaction, Replies.team_removed_player(team=owner_team, player=player))

    @group.command(name="list", description="Lists the players on a team")
    @app_commands.describe(team_name="The name of the team to list the players of")
    async def team_list(self, interaction: discord.Interaction, team_name: str = None):

        if team_name is not None:
            team: Optional[Team] = self._teams.get(team_name)
            if team is None:
                await self.reply_to(interaction, Replies.no_registered_team_with_name(team_name=team_name))
                return
        else:
            player: Player = interaction.user

            player_team: Optional[Team] = self.get_player_team(player)

            if player_team is None:
                await self.reply_to(interaction, Replies.player_not_on_a_team)
                return

            team: Team = player_team

        await self.reply_to(
            interaction, Replies.team_players_list(team=team, team_players=self.get_team_players(team))
        )

    @group.command(name="points", description="Displays a team's points")
    @app_commands.describe(team_name="The name of the team to display the points of")
    async def team_points(self, interaction: discord.Interaction, team_name: str = None):

        if team_name is not None:
            team: Optional[Team] = self._teams.get(team_name)
            if team is None:
                await self.reply_to(interaction, Replies.no_registered_team_with_name(team_name=team_name))
                return
        else:
            player: Player = interaction.user

            player_team: Optional[Team] = self.get_player_team(player)

            if player_team is None:
                await self.reply_to(interaction, Replies.player_not_on_a_team)
                return

            team: Team = player_team

        await self.reply_to(interaction, Replies.team_points_display(team=team))

    @group.command(name="leave", description="Leaves your current team")
    async def team_leave(self, interaction: discord.Interaction):
        player: Player = interaction.user

        current_team: Optional[Team] = self.get_player_team(player)

        if current_team is None:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return

        # if the player is the owner of the team, transfer the ownership to a random team member
        if current_team.is_owned_by(player):

            team_players: Collection[Player] = self.get_team_players(current_team)
            other_players = [team_player for team_player in team_players if team_player.id != current_team.owner_id]

            # check if there is at least one other player on the team to transfer the ownership to
            if len(other_players) >= 1:
                new_owner: Player = random.choice(other_players)

                current_team.transfer_ownership(new_owner)

                await self.notify(
                    new_owner, Replies.team_player_promoted_to_owner_notify(team=current_team, previous_owner=player)
                )
            else:
                # if the team becomes empty after the owner leaves, delete/remove it
                self._teams.pop(current_team.name)

        try:
            current_team.remove_player(player)
        except CannotRemoveTeamOwner:
            pass
        self._player_id_to_team_name.pop(player.id)

        self.save_data()

        await self.reply_to(interaction, Replies.player_left_team_successfully(team=current_team))


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCog(bot))
