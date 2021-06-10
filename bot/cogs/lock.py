from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord import VoiceState, Member

from data.lock_manager import lock_manager


class LockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        updates = lock_manager.check(member, before, after)
        for update in updates:
            if update[0] == "mute":
                await member.edit(mute=update[1])
            elif update[0] == "deafen":
                await member.edit(deafen=update[1])
            elif update[0] == "voice_channel":
                await member.edit(voice_channel=self.bot.get_channel(update[1]))

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
    async def lock_mute(self, ctx, user: Member, muted: bool):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.")
            return
        lock_manager.add(ctx, user.id, lock_type="mute", lock_value=muted)
        await ctx.send(
            f"User `{user.name}#{user.discriminator}` locked as {'muted' if muted else 'unmuted'}.",
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
    async def unlock(self, ctx, user: Member):
        if not ctx.guild:
            await ctx.send("This command can only be run in servers.")
            return
        lock_manager.remove(ctx, user.id, lock_type="mute")
        await ctx.send(
            f"User `{user.name}#{user.discriminator}` unlocked.",
            hidden=True,
        )


def setup(bot):
    bot.add_cog(LockCog(bot))