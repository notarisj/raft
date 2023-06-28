from typing import Dict, List


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


def get_servers_from_file(file_path: str) -> list[list[str]]:
    """
    Reads server information from a file and returns it as a list of server lists.
    The format of each line in the file should be: <ip>, <port>, <value>

    Args:
        file_path: The path of the file to read.

    Returns:
        A list of server lists, where each server list contains server information in
        the format [ip, port, value].

    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If there is an error while reading the file.
        ValueError: If there is an invalid line format in the file.
    """
    servers_list = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                data = line.strip().split(", ")
                if len(data) != 3:
                    raise ValueError(f"Invalid line format in file: {file_path}")

                server_info = [data[0], int(data[1]), int(data[2])]
                servers_list.append(server_info)

    except FileNotFoundError as e:
        print(f"Error: File not found: {file_path}")
        raise e
    except IOError as e:
        print(f"Error: Failed to read file: {file_path}")
        raise e
    except ValueError as e:
        print(f"Error: Invalid line format in file: {file_path}")
        raise e

    return servers_list


def read_data_to_index_from_file(file_path: str) -> List[str]:
    """
    Reads data from a file and returns it as a list of strings.

    Args:
        file_path: The path of the file to read.

    Returns:
        A list of strings, where each string represents a line of data read from the file.

    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If there is an error while reading the file.
    """
    data = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                data.append(line.strip())
    except FileNotFoundError as e:
        print(f"Error: File not found: {file_path}")
        raise e
    except IOError as e:
        print(f"Error: Failed to read file: {file_path}")
        raise e

    return data
