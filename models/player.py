import discord


class Player:

    def __init__(self, discord_user: discord.Member):
        self.discord_user: discord.Member = discord_user
        self.name: str = discord_user.display_name
        self.team_name: str | None = None

    @property
    def has_team(self):
        return self.team_name is not None

    def __eq__(self, other) -> bool:
        if isinstance(other, Player):
            return self.discord_user.id == other.discord_user.id

        return False

    def __repr__(self) -> str:
        return f"Player(name={self.name})"
