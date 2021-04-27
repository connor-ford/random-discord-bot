from discord.ext import commands
from discord_slash import cog_ext
import discord_slash
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option

from data.data_manager import data_manager
from bot import guild_ids


class KeywordsCog(commands.Cog):
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
        data_manager.load(ctx)
        data_manager.update(
            "keywords", {(f" {keyword} " if keyword_only else keyword): response}
        )
        await ctx.send(f"Added keyword `{keyword}` with repsonse `{response}`.")

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
        ],
    )
    async def _remove_keyword(self, ctx, keyword: str):
        data_manager.load(ctx)
        data_manager.remove("keywords", keyword)
        await ctx.send(f"Removed keyword `{keyword}`.")

    @cog_ext.cog_subcommand(
        name="list",
        description="Gets a list of keywords and their responses.",
        base="keywords",
    )
    async def _list_keywords(self, ctx):
        data_manager.load(ctx)
        keywords = data_manager.get("keywords")

        if not keywords:
            await ctx.send(
                f"There are no keywords for this {'server' if data_manager.id_type == 'guild' else 'DM'}."
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