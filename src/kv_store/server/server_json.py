import json


class ServerJSON:
    """
    Represents a JSON object used for communication between the server and clients.

    Attributes:
        commands (str): The commands to be executed.
    """

    def __init__(self, commands: str):
        """
        Initializes a ServerJSON object.

        Args:
            commands (str): The commands to be executed.
        """
        self.commands = commands

    def get_command_type(self) -> str:
        """
        Returns the type of the command.

        Returns:
            The type of the command as a string.
        """
        return self.commands.split(" ", 1)[0]

    def get_command_value(self) -> str:
        """
        Returns the value of the command.

        Returns:
            The value of the command as a string.
        """
        return self.commands.split(" ", 1)[1]

    def get_command_key(self) -> str:
        """
        Returns the key of the command.

        Returns:
            The key of the command as a string.
        """
        results = self.commands.split(" ", 3)
        key = results[1].replace(":", "").replace("\"", "")
        return key

    @classmethod
    def from_json(cls, json_data: dict) -> 'ServerJSON':
        """
        Creates a ServerJSON object from JSON data.

        Args:
            json_data: JSON data representing a ServerJSON object.

        Returns:
            An instance of ServerJSON created from the JSON data.
        """
        return cls(**json_data)

    def to_json(self) -> dict:
        """
        Converts the ServerJSON object to JSON format.

        Returns:
            The ServerJSON object in JSON format.
        """
        return {
            "commands": self.commands
        }


class ServerJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for ServerJSON objects.
    """
    def default(self, obj) -> dict:
        """
        Overrides the default method of JSONEncoder to handle ServerJSON objects.

        Args:
            obj: The object to be encoded.

        Returns:
            The JSON representation of the object.
        """
        if isinstance(obj, ServerJSON):
            return obj.to_json()
        return super().default(obj)
