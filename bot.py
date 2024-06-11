import discord
from discord.ext import commands

import config

client = commands.Bot(command_prefix=config.PREFIX, intents=config.INTENTS)


async def load_commands() -> None:
    for commands_file in config.COMMANDS_DIR.glob("*.py"):
        if commands_file.name != "__init__.py":
            command: str = f"{config.COMMANDS_DIR.relative_to(config.BASE_DIR)}.{commands_file.name.removesuffix('.py')}"

            await client.load_extension(command)

            print(f"[+] Loaded {command}")


@client.event
async def on_ready():
    await load_commands()

    await client.tree.sync()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

    print(f"\n[+] Logged in as {client.user}\n")

    print(f"Connected to {len(client.guilds)} server(s):")
    for guild in client.guilds:
        print(f"- {guild.name} ({guild.id}): {guild.member_count} members")


def main() -> None:
    client.run(config.TOKEN)


if __name__ == "__main__":
    main()
