from typing import Dict, List


def get_data_from_file(file_path: str) -> Dict[str, str]:
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
