import os
import random
from typing import Any

from src.logger import MyLogger

logger = MyLogger()


class CreateValues:
    """
    Utility class for creating data with specified properties and writing it to a file.
    """

    def __init__(self, data_map: Any, parameters_controller: Any) -> None:
        """
        Initializes an instance of CreateValues.

        Args:
            data_map: A dictionary mapping keys to value types.
            parameters_controller: An object that controls the parameters for data generation.
        """
        self.top_lvl_key_prefix = "key"
        self.created_file_path = "/home/giannis-pc/Desktop/raft/kv_store/resources/dataToIndex.txt"
        self.data_map = data_map
        self.parameters_controller = parameters_controller
        self.nested_value_possibility = 0.25

    def create_data(self) -> None:
        """
        Generates the data line by line and writes it to a file.
        """
        lines = []
        for i in range(self.parameters_controller.get_num_of_lines()):
            line = self.generate_line(i)
            lines.append(line)
        data = "\n".join(lines)
        self.write_to_file(data)

    def generate_line(self, index: int) -> str:
        """
        Generates a line of data with a top-level key and its corresponding value.

        Args:
            index (int): The index of the line.

        Returns:
            The generated line as a string.
        """
        top_level_key = f"{self.top_lvl_key_prefix}{index + 1}"
        value = self.generate_value(self.parameters_controller.get_max_nesting_level())
        line = f'"{top_level_key}": {value}'
        return line

    def generate_value(self, nesting_level: int) -> str:
        """
        Generates a value with nested key-value pairs based on the specified nesting level.

        Args:
            nesting_level (int): The current nesting level.

        Returns:
            The generated value as a string.
        """
        value_list = []
        num_keys_of_current_level = random.randint(0, self.parameters_controller.get_max_key_num_of_value())
        used_keys = []
        for _ in range(num_keys_of_current_level):
            new_key = self.get_accepted_key(list(self.data_map.keys()), used_keys)
            used_keys.append(new_key)
            key_value_pair = self.generate_key_value_pair(new_key, nesting_level)
            value_list.append(key_value_pair)
        value = " , ".join(value_list)
        return f"{{ {value} }}"

    def generate_key_value_pair(self, key: str, nesting_level: int) -> str:
        """
        Generates a key-value pair based on the specified key and nesting level.

        Args:
            key (str): The key of the pair.
            nesting_level (int): The current nesting level.

        Returns:
            The generated key-value pair as a string.
        """
        if nesting_level > 0 and self.add_nested_value():
            nested_value = self.generate_value(nesting_level - 1)
            return f'"{key}": {nested_value}'
        else:
            value_type = self.data_map.get(key)
            if value_type == "int":
                return f'"{key}": {random.randint(0, 100)}'
            elif value_type == "float":
                return f'"{key}": {random.uniform(0, 100)}'
            elif value_type == "string":
                max_length = self.parameters_controller.get_max_string_length()
                random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=max_length))
                return f'"{key}": "{random_string}"'
            else:
                logger.info(f"Warning: Invalid type '{value_type}' for key '{key}'. It should be 'int', 'float', "
                            f"or 'string'. Assuming 'int'.")
                return f'"{key}": {random.randint(0, 100)}'

    def add_nested_value(self) -> bool:
        """
        Determines whether to add a nested value based on the configured possibility.

        Returns:
            True if a nested value should be added, False otherwise.
        """
        return random.random() <= self.nested_value_possibility

    @staticmethod
    def get_accepted_key(key_set: Any, used_keys: Any) -> str:
        """
        Gets an available key that has not been used before.

        Args:
            key_set: The set of available keys.
            used_keys: The list of already used keys.

        Returns:
            The chosen key as a string.

        Raises:
            ValueError: If no available keys are found.
        """
        available_keys = [k for k in key_set if k not in used_keys]
        if not available_keys:
            raise ValueError("Error: No available keys to choose from.")
        return random.choice(available_keys)

    def write_to_file(self, data: str) -> None:
        """
        Writes the generated data to a file.

        Args:
            data (str): The data to be written.

        Raises:
            IOError: If an error occurs while writing to the file.
        """
        directory = os.path.dirname(self.created_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            with open(self.created_file_path, "w") as file:
                file.write(data)
            logger.info("Successfully wrote to the file.")
        except IOError as e:
            logger.info(f"Error: Failed to write to the file '{self.created_file_path}'. {str(e)}")
            exit(-1)
