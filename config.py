import os
import pathlib
from typing import Optional

from dotenv import load_dotenv
import discord

load_dotenv()

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.resolve()
COGS_DIR: pathlib.Path = BASE_DIR / "cogs"

TOKEN: Optional[str] = os.getenv("TOKEN")
PREFIX: str = '.'
INTENTS: discord.Intents = discord.Intents.default()
INTENTS.members = True
