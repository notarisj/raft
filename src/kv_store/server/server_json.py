import json


class ServerJSON:
    def __init__(self, sender, commands):
        self.sender = sender
        self.commands = commands

    def get_command_type(self):
        return self.commands.split(" ", 1)[0]

    def get_command_value(self):
        return self.commands.split(" ", 1)[1]

    def get_command_key(self):
        results = self.commands.split(" ", 3)
        key = results[1].replace(":", "").replace("\"", "")
        return key

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)

    def to_json(self):
        return {
            "sender": self.sender,
            "commands": self.commands
        }


# Custom JSON encoders for ServerJSON
class ServerJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ServerJSON):
            return obj.to_json()
        return super().default(obj)

