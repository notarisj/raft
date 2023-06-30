import json
from typing import List


class RaftJSON:
    """
    Represents a JSON object for the messages send to Raft consensus algorithm.
    It consists of the:
        - commands (array of commands)
        - replica IDs (servers that should execute the commands).
    """

    def __init__(self, commands: List[str], rep_ids: List[int]) -> None:
        """
        Initializes an instance of RaftJSON.

        Args:
            commands: The commands included in the JSON object.
            rep_ids: The IDs of the replicas associated with the JSON object.
        """
        self.commands = commands
        self.rep_ids = rep_ids

    @classmethod
    def from_json(cls, json_data: dict) -> 'RaftJSON':
        """
        Creates a RaftJSON object from a JSON dictionary.

        Args:
            json_data: The JSON dictionary.

        Returns:
            An instance of RaftJSON.
        """
        return cls(**json_data)

    def to_json(self) -> dict:
        """
        Converts the RaftJSON object to a JSON dictionary.

        Returns:
            The JSON dictionary representation of the RaftJSON object.
        """
        return {
            "commands": self.commands,
            "rep_ids": self.rep_ids
        }


class RaftJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for RaftJSON objects.
    """

    def default(self, obj) -> dict:
        """
        Overrides the default JSONEncoder behavior to handle RaftJSON objects.

        Args:
            obj: The object to encode.

        Returns:
            The JSON-compatible representation of the object.
        """
        if isinstance(obj, RaftJSON):
            return obj.to_json()
        return super().default(obj)
