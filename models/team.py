from dataclasses import dataclass, field


class PlayerAlreadyOnTheTeam(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} is already on the team \"{team_name}\"")


class PlayerNotOnTheTeam(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} is not on the team \"{team_name}\"")


class PlayerAlreadyIsOwner(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} already is the owner of the team \"{team_name}\"")


@dataclass(frozen=True)
class Team:
    """
    Represents a generic team of players.

    Attributes
    ========
    name - the team's name
    owner_id - the Discord ID of the team's owner
    guild_id - the ID of the Discord Guild where the team was created
    players - the list of the team's players Discord IDs
    points - the number of points the team has
    """

    name: str
    owner_id: int
    guild_id: int
    players: list[int] = field(default_factory=list)
    points: int = 0

    def __post_init__(self):
        self.add_player(self.owner_id)

    def add_player(self, player_id: int) -> None:
        """
        Adds a player to the team

        :param player_id: the Discord ID of the player to add to the team
        :raises PlayerAlreadyOnTheTeam: if the player is already on the team
        """

        if player_id in self.players:
            raise PlayerAlreadyOnTheTeam(player_id, self.name)

        self.players.append(player_id)

    def remove_player(self, player_id: int) -> None:
        """
        Removes a player from the team

        :param player_id: the Discord ID of the player to remove from the team
        :raises PlayerNotOnTheTeam: if the player is not in the team
        """

        if player_id not in self.players:
            raise PlayerNotOnTheTeam(player_id, self.name)

        self.players.remove(player_id)

    def transfer_ownership(self, new_owner_id: int) -> None:
        """
        Removes a player from the team

        :param new_owner_id: the Discord ID of the player to transfer the ownership to
        :raises PlayerNotOnTheTeam: if the player is not in the team
        :raises PlayerAlreadyIsOwner: if new_owner already is the team's owner
        """

        if new_owner_id not in self.players:
            raise PlayerNotOnTheTeam(new_owner_id, self.name)

        if self.owner_id == new_owner_id:
            raise PlayerAlreadyIsOwner(new_owner_id, self.name)

        object.__setattr__(self, "owner_id", new_owner_id)

    def is_owned_by(self, player_id: int) -> bool:
        """
        Checks if the team is owned by the given player

        :param player_id: the Discord ID of the player to check
        :return: `True` if the player is the owner of the team, `False` otherwise
        """
        return self.owner_id == player_id
