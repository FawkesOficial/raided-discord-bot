from dataclasses import dataclass, field


class PlayerAlreadyInTeam(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} is already in the team \"{team_name}\"")


class PlayerNotInTeam(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} is not on the team \"{team_name}\"")


class PlayerAlreadyIsOwner(Exception):

    def __init__(self, player_id: int, team_name: str):
        super().__init__(f"player {player_id} already is the owner of the team \"{team_name}\"")


@dataclass(frozen=True)
class Team:
    name: str
    owner_id: int
    players: list[int] = field(default_factory=list)
    points: int = 0

    def __post_init__(self):
        self.add_player(self.owner_id)

    def add_player(self, player_id: int) -> None:
        """
        Adds a player to the team

        :param player_id: the player to add to the team
        :raises PlayerAlreadyInTeam: if the player is already in the team
        """

        if player_id in self.players:
            raise PlayerAlreadyInTeam(player_id, self.name)

        self.players.append(player_id)

    def remove_player(self, player_id: int) -> None:
        """
        Removes a player from the team

        :param player_id: the player to remove from the team
        :raises PlayerNotInTeam: if the player is not in the team
        """

        if player_id not in self.players:
            raise PlayerNotInTeam(player_id, self.name)

        self.players.remove(player_id)

    def transfer_ownership(self, new_owner_id: int) -> None:
        """
        Removes a player from the team

        :param new_owner_id: the player to transfer the ownership to
        :raises PlayerNotInTeam: if the player is not in the team
        :raises PlayerAlreadyIsOwner: if new_owner already is the team's owner
        """

        if new_owner_id not in self.players:
            raise PlayerNotInTeam(new_owner_id, self.name)

        if self.owner_id == new_owner_id:
            raise PlayerAlreadyIsOwner(new_owner_id, self.name)

        object.__setattr__(self, "owner_id", new_owner_id)
