import asyncio
import os
import platform
import random
from datetime import datetime

import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from lib.consts import C_ERROR, PREFIX, TOKEN

intents = discord.Intents.default()

intents.members = True
intents.message_content = True
intents.presences = True

bot = Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)


@bot.event
async def on_ready() -> None:  # start processes

    bot.session = ClientSession(loop=bot.loop)
    bot.start_time = datetime.utcnow()
    print("loaded aiohttp session")
    print("-------------------")
    print(f"{bot.user.name}#{bot.user.discriminator}")
    print(f"discord.py {discord.__version__}")
    print(f"Python {platform.python_version()}")
    print(f"{platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    statuses = ["beep boop im a bot"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(context: Context, error) -> None:

    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="missing required argument",
            description=str(error).capitalize(),
            color=C_ERROR,
        )
        await context.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="no perms lmfao",
            description=f"required permission(s) `{', '.join(error.missing_permissions)}`",
            color=C_ERROR,
        )
        await context.send(embed=embed)

    elif isinstance(error, commands.NotOwner):

        embed = discord.Embed(title="not owner", description="no", color=C_ERROR)
        await context.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours, minutes, seconds = int(hours), int(minutes), int(seconds)
        embed = discord.Embed(
            title="command on cooldown",
            description="cooldown expires in "
            + (f"{hours} hours " if hours > 0 else "")
            + (f"{minutes} minutes " if minutes > 0 else "")
            + (f"{seconds} seconds" if seconds > 0 else ""),
            color=C_ERROR,
        )
        await context.send(embed=embed)

    raise error


async def load_cogs() -> None:

    for file in os.listdir("./bot/exts"):
        if file.endswith(".py"):
            ext = file[:-3]
            try:
                await bot.load_extension(f"exts.{ext}")
                print(f"'{ext}' loaded")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Exception on loading {ext}\n{exception}")


asyncio.run(load_cogs())

bot.run(TOKEN)
