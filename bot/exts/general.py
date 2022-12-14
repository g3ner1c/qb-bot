import discord
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import C_NEUTRAL, INVITE


class General(commands.Cog, name="general commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="ping",
        description="ping bot",
    )
    async def ping(self, context: Context) -> None:
        embed = discord.Embed(
            title="still alive!",
            description=f"latency: {round(self.bot.latency * 1000, 3)}ms.",
            color=C_NEUTRAL,
        )
        await context.send(embed=embed)

    @commands.command(
        name="invite",
        description="get invite link",
    )
    async def invite(self, context: Context) -> None:
        embed = discord.Embed(
            description=f"Invite me by clicking [here]({INVITE}).",
            color=C_NEUTRAL,
        )
        try:
            await context.author.send(embed=embed)
        except discord.Forbidden:
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
