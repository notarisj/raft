import json


class RaftJSON:
    def __init__(self, sender, commands, rep_ids):
        self.sender = sender
        self.commands = commands
        self.rep_ids = rep_ids

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)

    def to_json(self):
        return {
            "sender": self.sender,
            "commands": self.commands,
            "rep_ids": self.rep_ids
        }


# Custom JSON encoders for ServerJSON
class RaftJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RaftJSON):
            return obj.to_json()
        return super().default(obj)