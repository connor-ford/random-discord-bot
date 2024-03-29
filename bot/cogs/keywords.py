from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

from data.keyword_manager import keyword_manager


class KeywordsCog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        response = keyword_manager.check(message)
        if response:
            await message.channel.send(response)

    @cog_ext.cog_subcommand(
        name="add",
        description="Add a keyword and its response.",
        base="keywords",
        options=[
            create_option(
                name="keyword",
                description="The keyword, triggered when matched exactly.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="response",
                description="The message to send when the keyword is triggered.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="keyword_only",
                description="Determines if the keyword only matches when it is by itself.",
                option_type=SlashCommandOptionType.BOOLEAN,
                required=True,
            ),
        ],
    )
    async def _add_keyword(self, ctx, keyword: str, response: str, keyword_only: bool):
        keyword_manager.add(ctx, f" {keyword} " if keyword_only else keyword, response)
        await ctx.send(
            f"Added keyword `{keyword}` with repsonse `{response}`{' (Keyword only)' if keyword_only else ''}."
        )

    @cog_ext.cog_subcommand(
        name="remove",
        description="Remove a keyword.",
        base="keywords",
        options=[
            create_option(
                name="keyword",
                description="The keyword to remove.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="keyword_only",
                description="Determines if the keyword had the keyword_only flag.",
                option_type=SlashCommandOptionType.BOOLEAN,
                required=True,
            ),
        ],
    )
    async def _remove_keyword(self, ctx, keyword: str, keyword_only: bool):
        if not keyword_manager.remove(ctx, keyword, keyword_only):
            await ctx.send(
                f"Could not remove `{keyword}`{' (Keyword only)' if keyword_only else ''}."
            )
            return
        await ctx.send(
            f"Removed keyword `{keyword}`{' (Keyword only)' if keyword_only else ''}."
        )

    @cog_ext.cog_subcommand(
        name="list",
        description="Gets a list of keywords and their responses.",
        base="keywords",
    )
    async def _list_keywords(self, ctx):
        keywords = keyword_manager.list(ctx)

        if not keywords:
            await ctx.send(
                f"There are no keywords for this {'server' if keyword_manager.id_type == 'guild' else 'DM'}."
            )
            return

        message = (
            f"Listing {len(keywords)} keyword{'s' if len(keywords) > 1 else ''}:\n```"
        )
        for keyword, response in keywords.items():
            message += f'"{keyword.strip()}": "{response}"{" (Keyword only)" if keyword.startswith(" ") else ""}\n'
        message += "```"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(KeywordsCog(bot))
