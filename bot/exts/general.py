"""General commands."""

from datetime import datetime

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
    async def ping(self, ctx: Context) -> None:
        embed = discord.Embed(
            title="still alive!",
            description=f"latency: {round(self.bot.latency * 1000, 3)}ms.",
            color=C_NEUTRAL,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="invite",
        description="get invite link",
    )
    async def invite(self, ctx: Context) -> None:
        embed = discord.Embed(
            description=f"Invite me by clicking [here]({INVITE}).",
            color=C_NEUTRAL,
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=embed)

    @commands.command(
        name="end",
        description="ends a question or question session",
    )
    async def end(self, ctx: Context) -> None:
        # doesnt do anything just makes it look neat on >help
        pass

    @commands.command(
        name="uptime",
        description="get uptime info",
    )
    async def uptime(self, ctx: Context) -> None:
        embed = discord.Embed(title="Status", color=C_NEUTRAL)
        embed.add_field(name="Uptime", value=str(datetime.utcnow() - self.bot.start_time))
        embed.add_field(name="Last restart (UTC)", value=f"`{str(self.bot.start_time)}`")
        await ctx.send(embed=embed)

    @commands.command(
        name="github",
        description="get github link",
    )
    async def github(self, ctx: Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title="You can find my source code here!", url="https://github.com/g3ner1c/qb-bot"
            )
        )

    @commands.command(
        name="about",
        description="general info",
    )
    async def about(self, ctx: Context) -> None:
        embed = discord.Embed(title="About", color=C_NEUTRAL)
        embed.description = (
            "I'm an [open source](https://github.com/g3ner1c/qb-bot) quizbowl "
            "discord bot licensed under "
            "[AGPL-3.0](https://github.com/g3ner1c/qb-bot/blob/main/LICENSE).\n"
            "All data is fetched from [QB Reader](https://www.qbreader.org). \n\n"
            "Contributions are always welcome! \n Please feel free to [open issues]"
            "(https://github.com/g3ner1c/qb-bot/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)"
            " or pull requests with suggestions, bugfixes, etc."
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
