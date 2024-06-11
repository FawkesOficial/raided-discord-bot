import discord
from discord.ext import commands

import config

client = commands.Bot(command_prefix=config.PREFIX, intents=config.INTENTS)


async def load_cogs() -> None:
    for cog_file in config.COGS_DIR.glob("*.py"):
        if cog_file.name != "__init__.py":
            cog: str = f"{config.COGS_DIR.relative_to(config.BASE_DIR)}.{cog_file.name.removesuffix('.py')}"

            await client.load_extension(cog)

            print(f"[+] Loaded {cog}")


@client.event
async def on_ready():
    await load_cogs()

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
