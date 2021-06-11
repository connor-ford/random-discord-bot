from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord import VoiceState, Member, VoiceChannel, ChannelType

from data.lock_manager import lock_manager


class LockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        updates = lock_manager.check(member, after)
        for update in updates:
            if update[0] == "mute":
                await member.edit(mute=update[1])
            elif update[0] == "deafen":
                await member.edit(deafen=update[1])
            elif update[0] == "channel":
                await member.edit(voice_channel=await self.bot.fetch_channel(update[1]))

    @cog_ext.cog_subcommand(
        name="mute",
        description="Lock the specified user as muted or unmuted. This command can only be run in servers.",
        base="lock",
        options=[
            create_option(
                name="user",
                description="The user to lock.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
            create_option(
                name="muted",
                description="Determines if the user should be locked as muted or unmuted.",
                option_type=SlashCommandOptionType.BOOLEAN,
                required=True,
            ),
        ],
    )
    async def _lock_mute(self, ctx, user: Member, muted: bool):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.", hidden=True)
            return
        lock_manager.add(ctx, user.id, lock_type="mute", lock_value=muted)
        await ctx.send(
            f"User `{user}` locked as {'muted' if muted else 'unmuted'}.",
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        name="deafen",
        description="Lock the specified user as deafened or undeafened. This command can only be run in servers.",
        base="lock",
        options=[
            create_option(
                name="user",
                description="The user to lock.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
            create_option(
                name="deafened",
                description="Determines if the user should be locked as deafened or undeafened.",
                option_type=SlashCommandOptionType.BOOLEAN,
                required=True,
            ),
        ],
    )
    async def _lock_deafen(self, ctx, user: Member, deafened: bool):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.", hidden=True)
            return
        lock_manager.add(ctx, user.id, lock_type="deafen", lock_value=deafened)
        await ctx.send(
            f"User `{user}` locked as {'deafened' if deafened else 'undeafened'}.",
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        name="channel",
        description="Lock the specified user in a specified voice channel. This command can only be run in servers.",
        base="lock",
        options=[
            create_option(
                name="user",
                description="The user to lock.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
            create_option(
                name="channel",
                description="The voice channel to lock the user in.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def _lock_channel(self, ctx, user: Member, channel: VoiceChannel):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.", hidden=True)
            return
        if channel.type != ChannelType.voice:
            await ctx.send("The selected channel must be a voice channel.", hidden=True)
            return
        lock_manager.add(ctx, user.id, lock_type="channel", lock_value=str(channel.id))
        await ctx.send(
            f"User `{user}` locked in `{channel}` (ID {channel.id}).",
            hidden=True,
        )

    @cog_ext.cog_slash(
        name="unlock",
        description="Unlock the specified user. This command can only be run in servers.",
        options=[
            create_option(
                name="user",
                description="The user to unlock.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
        ],
    )
    async def _unlock(self, ctx, user: Member):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.")
            return
        lock_manager.remove(ctx, user.id)
        await ctx.send(
            f"User `{user}` unlocked.",
            hidden=True,
        )


def setup(bot):
    bot.add_cog(LockCog(bot))