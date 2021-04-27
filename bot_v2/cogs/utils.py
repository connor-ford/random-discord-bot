from discord.ext import commands
from discord_slash import cog_ext


class UtilsCog(commands.Cog):
    @cog_ext.cog_slash(
        name="ping", description="Get the latency of the bot, in milliseconds."
    )
    async def _ping(self, ctx):
        await ctx.send(f"Pong! ({(int) (ctx.bot.latency*1000)}ms)")


def setup(bot):
    bot.add_cog(UtilsCog(bot))