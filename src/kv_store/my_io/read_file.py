from typing import Dict


def get_data_from_file(file_path: str) -> Dict[str, str]:
    """
    Reads data from a file and returns it as a dictionary.

    Args:
        file_path: The path of the file to read.

    Returns:
        A dictionary containing the data read from the file, where each line in the file is treated as a key-value pair.

    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If there is an error while reading the file.
        ValueError: If there is an invalid line format in the file.
    """
    data_map = {}

    try:
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split()
                data_map[key] = value
    except FileNotFoundError as e:
        print(f"Error: File not found: {file_path}")
        raise e
    except IOError as e:
        print(f"Error: Failed to read file: {file_path}")
        raise e
    except ValueError as e:
        print(f"Error: Invalid line format in file: {file_path}")
        raise e

    return data_map
