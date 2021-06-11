import json
import os
from data.data_manager import data_manager


class KeywordManager:
    def __init__(self):
        self.keywords = {"user": {}, "guild": {}}
        for root, _, files in os.walk("data"):
            for name in [file for file in files if file.endswith(".json")]:
                filepath = os.path.join(root, name)
                with open(filepath) as f:
                    self.keywords[filepath.split("/")[1][:-1]][
                        name.split(".")[0]
                    ] = json.load(f).get("keywords", {})

    def add(self, ctx, keyword, response):
        self._check_id(ctx)
        if self.id not in self.keywords[self.id_type]:
            self.keywords[self.id_type][self.id] = {}
        self.keywords[self.id_type][self.id][keyword] = response
        data_manager.load(ctx)
        data_manager.update("keywords", {keyword: response})

    def remove(self, ctx, keyword, keyword_only):
        self._check_id(ctx)
        if (f" {keyword} " if keyword_only else keyword) not in self.keywords[
            self.id_type
        ][self.id]:
            return False
        self.keywords[self.id_type][self.id].pop(
            f" {keyword} " if keyword_only else keyword
        )
        data_manager.load(ctx)
        data_manager.remove("keywords", f" {keyword} " if keyword_only else keyword)
        return True

    def check(self, message):
        self._check_id(message)
        if (
            self.id not in self.keywords[self.id_type]
            or not self.keywords[self.id_type][self.id]
        ):
            return False
        for keyword, response in self.keywords[self.id_type][self.id].items():
            if keyword.lower() in f" {message.content.lower()} ":
                return response
        return False

    def list(self, ctx):
        self._check_id(ctx)
        data_manager.load(ctx)
        return data_manager.get("keywords")

    def _check_id(self, ctx):
        if ctx.guild:
            self.id = str(ctx.guild.id)
            self.id_type = "guild"
        else:
            self.id = str(ctx.author.id)
            self.id_type = "user"


keyword_manager = KeywordManager()
