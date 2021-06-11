import json
import logging
import os

logger = logging.getLogger(__name__)


class DataManager:
    # Get the value of a key from the loaded guild/user
    def get(self, data_key):
        return self.guild_data[data_key] if data_key in self.guild_data else None

    # Load a guild/user using ctx from JSON file
    def load(self, ctx):
        self.id = ctx.guild.id if ctx.guild else ctx.author.id
        self.id_type = "guild" if ctx.guild else "user"
        if not os.path.isfile(f"data/{self.id_type}s/{self.id}.json"):
            with open(f"data/{self.id_type}s/{self.id}.json", "w+") as f:
                self.guild_data = {}
                json.dump(self.guild_data, f)
            logger.info(f"Created new file for {self.id_type} {self.id}.")
            return
        with open(f"data/{self.id_type}s/{self.id}.json", "r") as f:
            self.guild_data = json.load(f)
        logger.info(f"Loaded {self.id_type} {self.id} from file.")

    # Remove a key from the specified data key in the current guild/user
    def remove(self, data_key, key):
        if data_key in self.guild_data:
            self.guild_data[data_key].pop(key)
            with open(f"data/{self.id_type}s/{self.id}.json", "w") as f:
                json.dump(self.guild_data, f)
            logger.info(f"Removed {self.id_type} data for {self.id}.")

    # Update the data of the specified data key in the current guild/user
    def update(self, data_key, guild_data):
        if data_key in self.guild_data:
            self.guild_data[data_key].update(guild_data)
        else:
            self.guild_data[data_key] = guild_data
        with open(f"data/{self.id_type}s/{self.id}.json", "w") as f:
            json.dump(self.guild_data, f)
        logger.info(f"Updated {self.id_type} data for {self.id}.")


data_manager = DataManager()
