import random
from typing import Optional, Collection, Iterable
from dataclasses import dataclass, field

import discord
from discord import app_commands
from discord.ext import commands

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
        self.players.append(self.owner_id)

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the team

        :param player: the player to add to the team
        :raises PlayerAlreadyOnTheTeam: if the player is already on the team
        """

        if player.id in self.players:
            raise PlayerAlreadyOnTheTeam(player, self)

        self.players.append(player.id)

    def remove_player(self, player: Player) -> None:
        """
        Removes a player from the team

        :param player: the player to remove from the team
        :raises PlayerNotOnTheTeam: if the player is not on the team
        """

        if player.id not in self.players:
            raise PlayerNotOnTheTeam(player, self)

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


class Replies:
    # Static messages
    no_teams_registered: str = "No teams registered."
    player_not_on_a_team: str = "You are not on a team!"
    player_not_team_owner: str = "You are not the team's owner!"

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
    def player_not_on_the_team(*, player: Player, team: Team) -> str:
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


class PlayerAlreadyOnATeam(Exception):

    def __init__(self, player: Player, current_team: Team):
        super().__init__(f"player {player.display_name} is already on a team \"{current_team.name}\"")

        self.player = player
        self.current_team: Team = current_team


class PlayerNotOnATeam(Exception):

    def __init__(self, player: Player):
        super().__init__(f"player {player.display_name} is not on a team")

        self.player = player


class PlayerNotTeamOwner(Exception):

    def __init__(self, player: Player, team: Team):
        super().__init__(f"player {player.display_name} is not the owner of \"{team.name}\"")

        self.player = player
        self.team = team


class TeamAlreadyExists(Exception):
    def __init__(self, team: Team):
        super().__init__(f"team with the name \"{team.name}\" already exits")

        self.team = team


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


class TeamManager:

    def __init__(self):
        self._teams: dict[str, Team] = dict()  # team_name -> Team
        self._player_id_to_team: dict[int, Team] = dict()  # player_id -> Team

    @property
    def teams(self) -> Collection[Team]:
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

        return self._player_id_to_team.get(player.id)

    def create_team(self, team_name: str, owner: Player, guild: discord.Guild) -> Team:
        """
        Attempts to create a new team and add it to the "teams" database.

        :param team_name: the name of the new team
        :param owner: the team's owner
        :param guild: the Discord Guild where the team is being created
        :returns: the created team
        :raises PlayerAlreadyOnATeam: if the owner is already on a team
        :raises TeamAlreadyExists: if the team already exists
        """

        current_team: Optional[Team] = self.get_player_team(owner)
        if current_team is not None:
            raise PlayerAlreadyOnATeam(owner, current_team)

        if team_name in self._teams:
            raise TeamAlreadyExists(self._teams[team_name])

        new_team: Team = Team(name=team_name, owner_id=owner.id, guild_id=guild.id)

        self._teams[team_name] = new_team
        self._player_id_to_team[owner.id] = new_team

        return new_team

    def disband_team(self, player: Player) -> Team:
        """
        Attempts to disband a player's team and remove it from the "teams" database.

        :param player: the player whose team is being disbanded
        :raises PlayerNotOnATeam: if the player is not on a team
        :raises PlayerNotTeamOwner: if the player is not the team's owner
        """

        current_team: Optional[Team] = self.get_player_team(player)

        if current_team is None:
            raise PlayerNotOnATeam(player)

        if not current_team.is_owned_by(player):
            raise PlayerNotTeamOwner(player, current_team)

        for team_player_id in current_team.players:
            self._player_id_to_team.pop(team_player_id)

        self._teams.pop(current_team.name)

        return current_team

    def transfer_ownership(self, current_owner: Player, new_owner: Player) -> Team:
        """
        Attempts to transfer the ownership of `current_owner`'s team to `new_owner`

        :param current_owner: the team's current owner
        :param new_owner: the team's new owner
        :raises PlayerNotOnATeam: if `current_owner` is not on a team
        :raises PlayerNotTeamOwner: if `current_owner` is not the team's owner
        :raises PlayerNotOnTheTeam: if `new_owner` is not the team
        :raises PlayerAlreadyIsOwner: if `new_owner` is already on the team's owner
        """

        current_team: Optional[Team] = self.get_player_team(current_owner)

        if current_team is None:
            raise PlayerNotOnATeam(current_owner)

        if not current_team.is_owned_by(new_owner):
            raise PlayerNotTeamOwner(current_owner, current_team)

        current_team.transfer_ownership(new_owner)

        return current_team

    def invite_player(self, player: Player, owner: Player) -> None:
        """
        Attempts to invite `player` to `owner`s team

        :param player: the player to invite
        :param owner: the owner of the team
        :raises PlayerNotOnATeam: if `owner` is not on a team
        :raises PlayerNotTeamOwner: if `owner` is not the team's owner
        :raises PlayerAlreadyOnTheTeam: if `player` is already on the team
        """

        owner_team: Optional[Team] = self.get_player_team(owner)

        if owner_team is None:
            raise PlayerNotOnATeam(owner)

        if not owner_team.is_owned_by(owner):
            raise PlayerNotTeamOwner(owner, owner_team)

        # TODO: DEBUG!!!! ADDING PLAYER WITHOUT PERMISSION FOR TESTING PURPOSES
        owner_team.add_player(player)
        self._player_id_to_team[player.id] = owner_team

    def remove_player_from_team(self, player: Player, owner: Player) -> None:
        """
        Attempts to remove `player` from `owner`s team

        :param player: the player to remove
        :param owner: the owner of the team
        :raises PlayerNotOnATeam: if `owner` is not on a team
        :raises PlayerNotTeamOwner: if `owner` is not the team's owner
        :raises PlayerNotOnTheTeam: if `player` is not on the team
        """

        owner_team: Optional[Team] = self.get_player_team(owner)

        if owner_team is None:
            raise PlayerNotOnATeam(owner)

        if not owner_team.is_owned_by(owner):
            raise PlayerNotTeamOwner(owner, owner_team)

        owner_team.remove_player(player)
        self._player_id_to_team.pop(player.id)


class TeamCog(commands.Cog, name="team"):
    """Team related commands."""

    group = app_commands.Group(name="team", description="Team related commands")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.team_manager: TeamManager = TeamManager()
        # TODO: self.team_manager.load_database()
        # TODO: maybe even create an admin command like /teams load to manually load the teams

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

    # Individual Commands
    @app_commands.command(name="teams", description="Lists all the existing teams")
    async def teams(self, interaction: discord.Interaction):
        teams: Collection[Team] = self.team_manager.teams

        if len(teams) > 0:
            await self.reply_to(interaction, Replies.teams_display(teams=teams))
        else:
            await self.reply_to(interaction, Replies.no_teams_registered)

    # /team Commands
    @group.command(name="create", description="Creates a new team")
    @app_commands.describe(name="The name of the team")
    async def team_create(self, interaction: discord.Interaction, name: str):
        player: Player = interaction.user

        try:
            created_team: Team = self.team_manager.create_team(name, player, interaction.guild)
            await self.reply_to(interaction, Replies.team_created(created_team=created_team))
        except PlayerAlreadyOnATeam as e:
            await self.reply_to(interaction, Replies.already_on_a_team(current_team=e.current_team))
        except TeamAlreadyExists as e:
            await self.reply_to(interaction, Replies.team_already_exists(team_name=name))

    @group.command(name="disband", description="Disbands/deletes your team")
    async def team_disband(self, interaction: discord.Interaction):
        owner: Player = interaction.user

        try:
            disbanded_team: Team = self.team_manager.disband_team(owner)
            await self.reply_to(interaction, Replies.team_disbanded_successfully(disbanded_team=disbanded_team))

            team_players: list[Player] = filter(
                lambda team_player: team_player is not None and team_player.id != disbanded_team.owner_id,
                map(interaction.guild.get_member, disbanded_team.players)
            )

            for team_player in team_players:
                await self.notify(
                    team_player,
                    Replies.team_disbanded_notify_player(previous_team=disbanded_team, previous_owner=owner)
                )

        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)

    @group.command(name="transfer_ownership", description="Transfers your team's ownership to a player on your team")
    @app_commands.describe(player="The player to transfer the ownership to")
    async def team_transfer_ownership(self, interaction: discord.Interaction, player: discord.Member):
        owner: Player = interaction.user

        try:
            team: Team = self.team_manager.transfer_ownership(owner, player)
            await self.reply_to(interaction, Replies.ownership_transferred_successfully(team=team, new_owner=player))
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
        except PlayerNotOnTheTeam as e:
            await self.reply_to(interaction, Replies.player_not_on_the_team(player=player, team=e.team))

    @group.command(name="invite", description="Invites a player to your team")
    @app_commands.describe(player="The player to invite")
    async def team_invite(self, interaction: discord.Interaction, player: discord.Member):
        owner: Player = interaction.user

        try:
            self.team_manager.invite_player(player, owner)
            # TODO: send message to invitee, notifying them that they have been invited to a team
            # TODO: with buttons for "Accept" and "Reject"
            await self.reply_to(interaction, Replies.invited_player(player=player))
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
        except PlayerAlreadyOnTheTeam as e:
            await self.reply_to(interaction, Replies.player_already_on_the_team(player=e.player, team=e.team))

        # TODO: missing case where `player` is already on a team. in this case, they should still receive an invite
        # TODO: but be informed that they are already on a team

    @group.command(name="remove", description="Removes a player from your team")
    @app_commands.describe(player="The player to remove")
    async def team_remove(self, interaction: discord.Interaction, player: discord.Member):
        owner: Player = interaction.user

        try:
            self.team_manager.remove_player_from_team(player, owner)

            owner_team: Team = self.team_manager.get_player_team(owner)

            await self.notify(player, Replies.team_player_removed_notify(team=owner_team))

            await self.reply_to(interaction, Replies.team_removed_player(team=owner_team, player=player))
        except PlayerNotOnATeam:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
        except PlayerNotTeamOwner:
            await self.reply_to(interaction, Replies.player_not_team_owner)
        except PlayerNotOnTheTeam:
            owner_team: Team = self.team_manager.get_player_team(owner)

            await self.reply_to(interaction, Replies.player_not_on_the_team(player=player, team=owner_team))

    # TODO: make this able to list other team's players as well
    @group.command(name="list", description="Lists the players on your team")
    async def team_list(self, interaction: discord.Interaction):
        player: Player = interaction.user

        player_team: Optional[Team] = self.team_manager.get_player_team(player)

        if player_team is None:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return

        team_players: list[Player] = filter(
            lambda team_player: team_player is not None, map(interaction.guild.get_member, player_team.players)
        )

        await self.reply_to(interaction, Replies.team_players_list(team=player_team, team_players=team_players))

    # TODO: make this able to display other team's points as well
    @group.command(name="points", description="Displays your team's points")
    async def team_points(self, interaction: discord.Interaction):
        player: Player = interaction.user

        player_team: Optional[Team] = self.team_manager.get_player_team(player)

        if player_team is None:
            await self.reply_to(interaction, Replies.player_not_on_a_team)
            return

        await self.reply_to(interaction, Replies.team_points_display(team=player_team))

    @group.command(name="leave", description="Leaves your current team")
    async def team_leave(self, interaction: discord.Interaction):
        player: Player = interaction.user

        # check if player is not on a team
        current_team: Optional[Team] = self.get_team(player.id)
        if current_team is None:
            await interaction.response.send_message("You are not on a team!", ephemeral=True)
            return

        # if the player is the owner of the team, transfer the ownership to a random team member
        if current_team.owner_id == player.id:

            # check if there is at least one other player on the team to transfer the ownership to
            other_player_ids: list[int] = [
                player_id for player_id in current_team.players if player_id != current_team.owner_id
            ]
            if len(other_player_ids) > 0:
                new_owner_id: int = random.choice(other_player_ids)
                new_owner: Optional[Player] = interaction.guild.get_member(new_owner_id)

                if new_owner is not None:
                    previous_owner: Optional[Player] = interaction.guild.get_member(current_team.owner_id)

                    current_team.transfer_ownership(new_owner_id)
                    try:
                        await new_owner.send(
                            f"{previous_owner.display_name} left the team you are on ({current_team.name}). "
                            "You are now the team's owner!"
                        )
                    except discord.Forbidden:
                        # user doesn't allow messages from bots or private servers
                        pass

            else:
                # if the team becomes empty after the owner leaves, delete/remove it
                self.teams.pop(current_team.name)

        current_team.remove_player(player.id)
        self.player_id_to_team.pop(player.id)

        await interaction.response.send_message(f"Successfully left \"{current_team.name}\"", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCog(bot))
