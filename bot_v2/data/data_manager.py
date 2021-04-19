import json, os
import logging

logger = logging.getLogger(__name__)


class DataManager:
    def load(self, ctx):
        self.id = ctx.guild.id if ctx.guild else ctx.author.id
        self.id_type = "guild" if ctx.guild else "user"
        if not os.path.isfile(f"data/{self.id_type}s/{self.id}.json"):
            with open(f"data/{self.id_type}s/{self.id}.json", "w+") as f:
                json.dump({}, f)
                self.guild_data = {}
            logger.info(f"Created new file for {self.id_type} {self.id}.")
            return
        with open(f"data/{self.id_type}s/{self.id}.json", "r") as f:
            self.guild_data = json.load(f)
        logger.info(f"Loaded {self.id_type} {self.id} from file.")

    def get(self):
        return self.guild_data

    def update(self, guild_data):
        self.guild_data.update(guild_data)
        with open(f"data/{self.id_type}s/{self.id}.json", "w") as f:
            json.dump(self.guild_data, f)
        logger.info(f"Updated {self.id_type} data for {self.id}.")


data_manager = DataManager()