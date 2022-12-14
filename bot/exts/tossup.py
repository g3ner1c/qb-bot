import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import C_ERROR, C_NEUTRAL, C_SUCCESS

# import sqlite3
# from contextlib import closing


class Tossup(commands.Cog, name="tossup commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tossup",
        description="returns a random tossup",
    )
    async def tossup(self, context: Context) -> None:

        # return a random tossup from the database

        # with closing(sqlite3.connect('questions.db')) as sql:

        #     sql.row_factory = sqlite3.Row
        #     cur = sql.cursor()

        #     tossup = cur.execute('SELECT * FROM tossups ORDER BY RANDOM() LIMIT 1;').fetchone()

        api = "https://www.qbreader.org/api/random-question"

        params = {"questionType": "tossup"}

        tossup = requests.post(api, json=params).json()[0]

        embed = discord.Embed(title="Tossup", description=tossup["question"], color=C_NEUTRAL)
        await context.send(embed=embed)

        answer = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == context.author
            and message.channel == context.channel,
            timeout=60,
        )

        if answer.content.lower() in tossup["answer"].lower():
            await context.send(embed=discord.Embed(title="correct", color=C_SUCCESS))
        else:
            await context.send(embed=discord.Embed(title=answer, color=C_ERROR))


async def setup(bot):
    await bot.add_cog(Tossup(bot))
