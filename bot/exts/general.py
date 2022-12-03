import discord
from const import C_NEUTRAL
from discord.ext import commands
from discord.ext.commands import Context


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
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id=1026526068078805003&scope=bot+applications.commands&permissions=8).",
            color=C_NEUTRAL,
        )
        try:
            await context.author.send(embed=embed)
        except discord.Forbidden:
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
