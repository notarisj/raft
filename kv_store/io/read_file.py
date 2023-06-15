from typing import Dict, List
from kv_store.client.server_node import ServerInfo


class ReadFile:
    @staticmethod
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

    @staticmethod
    def get_servers_from_file(file_path: str) -> List[ServerInfo]:
        servers_list = []

        try:
            with open(file_path, "r") as file:
                for line in file:
                    host, port = line.strip().split()
                    try:
                        port = int(port)
                        server_info = ServerInfo(host, port)
                        servers_list.append(server_info)
                    except ValueError as e:
                        print(f"Error: Invalid port value in file: {file_path}")
                        raise e
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

    @staticmethod
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
