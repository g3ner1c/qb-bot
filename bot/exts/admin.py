"""Developer commands."""

import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context
from lib.consts import C_ERROR, C_SUCCESS


class Admin(commands.Cog, name="admin and dev testing commands"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.command(
        name="kill",
        description="kill bot",
    )
    @commands.is_owner()
    async def shutdown(self, ctx: Context) -> None:
        embed = discord.Embed(description="bot killed by owner", color=C_SUCCESS)
        await ctx.send(embed=embed)
        await self.bot.session.close()
        await self.bot.close()

    @commands.group(
        name="ext",
        description="manage extensions",
    )
    async def cog(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="No subcommand provided",
                description="Please specify a subcommand",
                color=C_ERROR,
            )
            await ctx.send(embed=embed)

    @cog.command(
        name="load",
        description="load extensions",
    )
    @commands.is_owner()
    async def load(self, ctx: Context, *exts: str) -> None:

        if len(exts) == 1 and exts[0] == "*":
            exts = [ext[:-3] for ext in os.listdir("./bot/exts") if ext.endswith(".py")]

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
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(title="Load", description=f"Loaded `{ext}`", color=C_SUCCESS)
            await ctx.send(embed=embed)

    @cog.command(
        name="unload",
        description="unload extensions",
    )
    @commands.is_owner()
    async def unload(self, ctx: Context, *exts: str) -> None:

        if len(exts) == 1 and exts[0] == "*":
            exts = [ext[:-3] for ext in os.listdir("./bot/exts") if ext.endswith(".py")]

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
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(title="Unload", description=f"Unloaded `{ext}`", color=C_SUCCESS)
            await ctx.send(embed=embed)

    @cog.command(
        name="reload",
        description="reload extensions",
    )
    @commands.is_owner()
    async def reload(self, ctx: Context, *exts: str) -> None:

        if len(exts) == 1 and exts[0] == "*":
            exts = [ext[:-3] for ext in os.listdir("./bot/exts") if ext.endswith(".py")]

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
                await ctx.send(embed=embed)
                return
            embed = discord.Embed(title="Reload", description=f"Reloaded `{ext}`", color=C_SUCCESS)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
