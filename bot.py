import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()

client = commands.Bot(command_prefix='.', intents=intents)

command = client.tree.command


@client.event
async def on_ready():
    await client.tree.sync()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

    print(f"\n[+] Logged in as {client.user}\n")

    print(f"Connected to {len(client.guilds)} server(s):")
    for guild in client.guilds:
        print(f"- {guild.name} ({guild.id}): {guild.member_count} members")


def main() -> None:
    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
