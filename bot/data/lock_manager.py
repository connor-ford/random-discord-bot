import json, os
from discord import VoiceState, Member
from data.data_manager import data_manager


class LockManager:
    def __init__(self):
        self.locks = {}
        for root, _, files in os.walk("data/guilds"):
            for name in [file for file in files if file.endswith(".json")]:
                filepath = os.path.join(root, name)
                with open(filepath) as f:
                    self.locks[
                        name.split(".")[0]
                    ] = json.load(f).get("locks")

    def add(self, ctx, id, lock_type: str, lock_value):
        self.id = str(id)
        if self.id not in self.locks:
            self.locks[str(ctx.guild.id)][self.id] = {}
        self.locks[str(ctx.guild.id)][self.id][lock_type] = lock_value
        data_manager.load(ctx)
        data_manager.update("locks", {id: {lock_type: lock_value}})

    def remove(self, ctx, id):
        self.id = str(id)
        self.locks.pop(self.id)
        data_manager.load(ctx)
        data_manager.remove("locks", self.id)
        return True

    def check(self, member: Member, before: VoiceState, after: VoiceState):
        self.id = str(member.id)
        if self.id not in self.locks[str(member.guild.id)]:
            return []
        updates = []
        for lock_type, lock_value in self.locks[str(member.guild.id)][self.id].items():
            if (
                (lock_type == "mute" and after.mute != lock_value)
                or (lock_type == "deafen" and after.deaf != lock_value)
                or (lock_type == "channel_move" and before.channel != after.channel)
            ):
                updates.append([lock_type, lock_value])
        return updates


lock_manager = LockManager()