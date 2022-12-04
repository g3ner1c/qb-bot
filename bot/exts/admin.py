from const import C_ERROR, C_SUCCESS
import discord
from discord.ext import commands
from discord.ext.commands import Context

# import sqlite3
# from contextlib import closing


class Admin(commands.Cog, name="admin and dev testing commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="kill",
        description="kill bot",
    )
    @commands.is_owner()
    async def shutdown(self, context: Context) -> None:
        embed = discord.Embed(description="bot killed by owner", color=C_SUCCESS)
        await context.send(embed=embed)
        await self.bot.close()

    # @commands.command(
    #     name="sql",
    #     description="query sql",
    # )
    # @commands.is_owner()
    # async def sql(self, context: Context, *, query: str) -> None:
    #     with closing(sqlite3.connect("questions.db")) as sql:
    #         cur = sql.cursor()

    #         await context.send(
    #             "\n".join(["`{}`".format(row) for row in cur.execute(query).fetchall()])
    #         )

    @commands.group(
        name="ext",
        description="manage extensions",
    )
    async def cog(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="No subcommand provided",
                description="Please specify a subcommand",
                color=C_ERROR,
            )
            await context.send(embed=embed)

    @cog.command(
        name="load",
        description="load extensions",
    )
    @commands.is_owner()
    async def load(self, context: Context, *exts: str) -> None:

        for ext in exts:

            try:
                await self.bot.load_extension(f"exts.{ext}")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                embed = discord.Embed(
                    title=f"Exception on loading {ext}",
                    description=f"{exception}",
                    color=C_ERROR,
                )
                await context.send(embed=embed)
                return

            embed = discord.Embed(title="Load", description=f"Loaded `{ext}`", color=C_SUCCESS)
            await context.send(embed=embed)

    @cog.command(
        name="unload",
        description="unload extensions",
    )
    @commands.is_owner()
    async def unload(self, context: Context, *exts: str) -> None:

        for ext in exts:

            try:
                await self.bot.unload_extension(f"exts.{ext}")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                embed = discord.Embed(
                    title=f"Exception on unloading {ext}",
                    description=f"{exception}",
                    color=C_ERROR,
                )
                await context.send(embed=embed)
                return
            embed = discord.Embed(title="Unload", description=f"Unloaded `{ext}`", color=C_SUCCESS)
            await context.send(embed=embed)

    @cog.command(
        name="reload",
        description="reload extensions",
    )
    @commands.is_owner()
    async def reload(self, context: Context, *exts: str) -> None:

        for ext in exts:

            try:
                await self.bot.reload_extension(f"exts.{ext}")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                embed = discord.Embed(
                    title=f"Exception on reloading {ext}",
                    description=f"{exception}",
                    color=C_ERROR,
                )
                await context.send(embed=embed)
                return
            embed = discord.Embed(title="Reload", description=f"Reloaded `{ext}`", color=C_SUCCESS)
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
