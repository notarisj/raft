from typing import List

from src.logger import MyLogger

logger = MyLogger()


class ParametersController:
    """
    A class that manages and provides access to various parameters.

    Attributes:
        key_file_path (str): The path to the key file.
        num_of_lines (int): The number of lines.
        max_nesting_level (int): The maximum nesting level.
        max_key_num_of_value (int): The maximum number of keys inside values.
        max_string_length (int): The maximum length of a string.
    """

    def __init__(self) -> None:
        """
        Initializes an instance of ParametersController with default parameter values.
        """
        self.key_file_path = ""
        self.num_of_lines = 0
        self.max_nesting_level = 0
        self.max_key_num_of_value = 0
        self.max_string_length = 0

    def read_parameters(self, args: List[str]) -> None:
        """
        Reads and assigns the parameters from the command line arguments.

        Args:
            args (list): The list of command line arguments.

        Raises:
            ValueError: If the number of parameters is incorrect.
        """
        if len(args) != 11:
            raise ValueError("Error: Incorrect number of parameters. Expected 10, got {}".format(len(args)))
        self.assign_parameters(args)

    def assign_parameters(self, args: List[str]) -> None:
        """
        Assigns the parameter values based on the command line arguments.

        Args:
            args (list): The list of command line arguments.

        Raises:
            ValueError: If an invalid parameter flag is encountered or if a value fails to convert to an integer.
        """
        for i in range(1, len(args), 2):
            flag = args[i]
            value = args[i + 1]
            try:
                if flag == "-k":
                    self.key_file_path = value
                elif flag == "-n":
                    self.num_of_lines = int(value)
                elif flag == "-d":
                    self.max_nesting_level = int(value)
                elif flag == "-m":
                    self.max_key_num_of_value = int(value)
                elif flag == "-l":
                    self.max_string_length = int(value)
                else:
                    raise ValueError("Error: Invalid parameter flag: {}".format(flag))
            except ValueError:
                raise ValueError(
                    "Error: Failed to convert value '{}' for parameter flag '{}' to an integer".format(value, flag))

    def get_key_file_path(self) -> str:
        """
        Returns the key file path.

        Returns:
            str: The key file path.
        """
        return self.key_file_path

    def get_num_of_lines(self) -> int:
        """
        Returns the number of lines.

        Returns:
            int: The number of lines.
        """
        return self.num_of_lines

    def get_max_nesting_level(self) -> int:
        """
        Returns the maximum nesting level.

        Returns:
            int: The maximum nesting level.
        """
        return self.max_nesting_level

    def get_max_key_num_of_value(self) -> int:
        """
        Returns the maximum number of keys inside values.

        Returns:
            int: The maximum number of keys inside values.
        """
        return self.max_key_num_of_value

    def set_max_key_num_of_value(self, new_size: int):
        """
        Sets the maximum number of keys inside values.

        If the new size is smaller than the current value, a warning message is logged.

        Args:
            new_size (int): The new maximum size.

        """
        if new_size < self.max_key_num_of_value:
            logger.info("Warning: The max number of keys inside values must not be greater than the number of keys. "
                        "Changing value from {} to {}".format(self.max_key_num_of_value, new_size))
            self.max_key_num_of_value = new_size

    def get_max_string_length(self) -> int:
        """
        Returns the maximum length of a string.

        Returns:
            int: The maximum length of a string.
        """
        return self.max_string_length
