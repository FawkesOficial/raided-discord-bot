from typing import List

from models.player import Player


class PlayerAlreadyInTeam(Exception):

    def __init__(self, player: Player, team_name: str):
        super().__init__(f"player {player.name} is already in the team \"{team_name}\"")


class PlayerNotInTeam(Exception):

    def __init__(self, player: Player, team_name: str):
        super().__init__(f"player {player.name} is not on the team \"{team_name}\"")


class PlayerAlreadyIsOwner(Exception):

    def __init__(self, player: Player, team_name: str):
        super().__init__(f"player {player.name} already is the owner of the team \"{team_name}\"")


class Team:

    def __init__(self, name: str, owner: Player):
        self.name: str = name
        self.players: List[Player] = []
        self.points: int = 0
        self.owner: Player = owner

        self.add_player(owner)

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the team

        :param player: the player to add to the team
        :raises PlayerAlreadyInTeam: if the player is already in the team
        """

        if player in self.players:
            raise PlayerAlreadyInTeam(player, self.name)

        self.players.append(player)

    def remove_player(self, player: Player) -> None:
        """
        Removes a player from the team

        :param player: the player to remove from the team
        :raises PlayerNotInTeam: if the player is not in the team
        """

        if player not in self.players:
            raise PlayerNotInTeam(player, self.name)

        self.players.remove(player)

    def transfer_ownership(self, new_owner: Player) -> None:
        """
        Removes a player from the team

        :param new_owner: the player to transfer the ownership to
        :raises PlayerNotInTeam: if the player is not in the team
        :raises PlayerAlreadyIsOwner: if new_owner already is the team's owner
        """

        if new_owner not in self.players:
            raise PlayerNotInTeam(new_owner, self.name)

        if self.owner == new_owner:
            raise PlayerAlreadyIsOwner(new_owner, self.name)

        self.owner = new_owner

    def __repr__(self) -> str:
        return f"Team(name={self.name}, players={self.players}, points={self.points}, owner={self.owner})"
