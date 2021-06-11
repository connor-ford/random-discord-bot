import json
import os
from discord import VoiceState, Member
from data.data_manager import data_manager


class LockManager:
    def __init__(self):
        self.locks = {}
        for root, _, files in os.walk("data/guilds"):
            for name in [file for file in files if file.endswith(".json")]:
                filepath = os.path.join(root, name)
                with open(filepath) as f:
                    self.locks[name.split(".")[0]] = json.load(f).get("locks", {})
        print(self.locks)

    def add(self, ctx, id, lock_type: str, lock_value):
        self.id = str(id)
        self.guild_id = str(ctx.guild.id)
        if self.guild_id not in self.locks:
            self.locks[self.guild_id] = {}
        if self.id not in self.locks[self.guild_id]:
            self.locks[self.guild_id][self.id] = {}
        self.locks[self.guild_id][self.id].update({lock_type: lock_value})
        data_manager.load(ctx)
        data_manager.update("locks", self.locks[self.guild_id])

    def remove(self, ctx, id):
        self.id = str(id)
        self.guild_id = str(ctx.guild.id)
        if self.guild_id in self.locks and self.id in self.locks[self.guild_id]:
            self.locks[self.guild_id].pop(self.id)
        data_manager.load(ctx)
        data_manager.remove("locks", self.id)
        return True

    def check(self, member: Member, voice_state: VoiceState):
        self.id = str(member.id)
        if self.id not in self.locks[str(member.guild.id)]:
            return []
        updates = []
        for lock_type, lock_value in self.locks[str(member.guild.id)][self.id].items():
            if (
                (lock_type == "mute" and voice_state.mute != lock_value)
                or (lock_type == "deafen" and voice_state.deaf != lock_value)
                or (
                    lock_type == "channel"
                    and voice_state.channel
                    and str(voice_state.channel.id) != lock_value
                )
            ):
                updates.append([lock_type, lock_value])
        return updates

    def list(self, guild_id: str):
        return self.locks[guild_id] if guild_id in self.locks else {}


lock_manager = LockManager()
