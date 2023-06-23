import configparser
import json


class IniConfig:
    def __init__(self, ini_file):
        """
        Initializes an IniConfig object.

        Args:
            ini_file (str): The path to the INI configuration file.

        Returns:
            None
        """
        self.config = configparser.ConfigParser()
        self.config.read(ini_file)

    def get_property(self, section, key):
        """
        Retrieves a property value from the INI configuration.

        Args:
            section (str): The section in the INI file.
            key (str): The key of the property.

        Returns:
            The value of the property.
        """
        return self.config.get(section, key)

    def get_all_properties(self, section):
        """
        Retrieves all properties within a section of the INI configuration.

        Args:
            section (str): The section in the INI file.

        Returns:
            dict: A dictionary containing all properties within the section.
        """
        return dict(self.config.items(section))

    def save(self, ini_file):
        """
        Saves the INI configuration to a file.

        Args:
            ini_file (str): The path to save the INI configuration.

        Returns:
            None
        """
        with open(ini_file, 'w') as f:
            self.config.write(f)


class JsonConfig:
    def __init__(self, json_file):
        """
        Initializes a JsonConfig object.

        Args:
            json_file (str): The path to the JSON configuration file.

        Returns:
            None
        """
        with open(json_file) as f:
            self.config = json.load(f)

    def get_property(self, key):
        """
        Retrieves a property value from the JSON configuration.

        Args:
            key (str): The key of the property.

        Returns:
            The value of the property.
        """
        return self.config.get(key)

    def get_all_properties(self):
        """
        Retrieves all properties within the JSON configuration.

        Returns:
            dict: The JSON configuration as a dictionary.
        """
        return self.config

    def save(self, json_file):
        """
        Saves the JSON configuration to a file.

        Args:
            json_file (str): The path to save the JSON configuration.

        Returns:
            None
        """
        with open(json_file, 'w') as f:
            json.dump(self.config, f)
