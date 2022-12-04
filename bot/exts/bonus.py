import discord
import requests
from const import C_NEUTRAL, C_ERROR, C_SUCCESS
from discord.ext import commands
from discord.ext.commands import Context


class Bonus(commands.Cog, name="bonus commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="bonus",
        description="returns a random bonus",
    )
    async def bonus(self, context: Context) -> None:

        api = "https://www.qbreader.org/api/random-question"

        params = {"questionType": "bonus"}

        bonus = requests.post(api, json=params).json()[0]

        points = 0

        leadin = discord.Embed(
            title="Bonus", description=bonus["leadin"], color=C_NEUTRAL
        )
        await context.send(embed=leadin)

        for i, (q, a) in enumerate(zip(bonus["parts"], bonus["answers"]), 1):

            part = discord.Embed(title=str(i), description=q, color=C_NEUTRAL)

            await context.send(embed=part)

            answer = await self.bot.wait_for(
                "message",
                check=lambda message: message.author == context.author
                and message.channel == context.channel,
                timeout=60,
            )

            if answer.content.lower() in a.lower():
                await context.send(
                    embed=discord.Embed(title="correct", color=C_SUCCESS)
                )
                points += 10
            else:
                await context.send(embed=discord.Embed(title=a, color=C_ERROR))

        await context.send(
            embed=discord.Embed(
                title=f"{points}/{10*len(bonus['parts'])}", color=C_NEUTRAL
            )
        )


async def setup(bot):
    await bot.add_cog(Bonus(bot))
