import asyncio
from asyncio import Lock

import discord
from discord.ext import commands
from discord.ext.commands import Context
from lib.consts import C_ERROR, C_NEUTRAL, C_SUCCESS
from lib.utils import parse_int_range, parse_subcats, tossup_read

lock = Lock()


class Tossup(commands.Cog, name="tossup commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tossup",
        description="returns a random tossup",
    )
    async def tossup(self, ctx: Context, *argv) -> None:

        api = "https://www.qbreader.org/api/random-question"

        params = {"questionType": "tossup"}

        diffs = []
        cats = []

        for arg in argv:

            if any(char.isdecimal() for char in arg):
                diffs.append(arg)

            elif arg.isalpha():
                cats.append(arg)

            else:
                await ctx.send(embed=discord.Embed(title="invalid argument", color=C_ERROR))
                return

        if diffs:
            params["difficulties"] = parse_int_range(diffs)

        if cats:
            params["subcategories"] = parse_subcats(cats)

        async with self.bot.session.post(api, json=params) as r:
            tossup = (await r.json(content_type="text/html"))[0]

        tossup_parts = tossup_read(tossup["question"], 5)

        embed = discord.Embed(title="Tossup", description="", color=C_NEUTRAL)
        tu = await ctx.send(embed=embed)

        print(tossup["answer"])

        async def edit_tossup():

            for i in range(len(tossup_parts)):

                async with lock:

                    embed = discord.Embed(
                        title="Tossup", description=tossup_parts[i], color=C_NEUTRAL
                    )
                    print("sending")
                    await tu.edit(embed=embed)
                    print("sent")

                await asyncio.sleep(0.8)

        read = asyncio.create_task(edit_tossup())

        async def listen_for_answer():

            await self.bot.wait_for(
                "message",
                check=lambda message: message.author == ctx.author
                and message.channel == ctx.channel
                and not message.content.startswith("_"),
                timeout=60,
            )

            async with lock:

                print("buzz")

                await ctx.send(
                    embed=discord.Embed(
                        title="Buzz",
                        description=f"from {ctx.author.mention}",
                        color=C_SUCCESS,
                    )
                )

                try:
                    answer = await self.bot.wait_for(
                        "message",
                        check=lambda message: message.author == ctx.author
                        and message.channel == ctx.channel,
                        timeout=5,
                    )

                except asyncio.TimeoutError:
                    await ctx.send(embed=discord.Embed(title="no answer", color=C_ERROR))
                    print("no answer")
                    read.cancel()
                    await tu.edit(
                        embed=discord.Embed(
                            title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                        )
                    )
                    await ctx.send(embed=discord.Embed(title=tossup["answer"], color=C_NEUTRAL))
                    return

                if answer.content.lower() in tossup["answer"].lower():
                    await ctx.send(embed=discord.Embed(title="correct", color=C_SUCCESS))
                    print("correct")
                else:
                    await ctx.send(embed=discord.Embed(title="incorrect", color=C_ERROR))
                    print("incorrect")

                read.cancel()
                await tu.edit(
                    embed=discord.Embed(
                        title="Tossup", description=tossup_parts[-1], color=C_NEUTRAL
                    )
                )
                await ctx.send(embed=discord.Embed(title=tossup["answer"], color=C_NEUTRAL))
                return

        asyncio.create_task(listen_for_answer())


async def setup(bot):
    await bot.add_cog(Tossup(bot))
