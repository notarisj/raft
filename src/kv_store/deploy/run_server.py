import argparse
from src.configuration_reader.read_config import IniConfig, JsonConfig
from src.kv_store.server import KVServer

"""
This script is used to run a key-value server.
"""


def parse_arguments():
    """
    Parses the arguments passed to the script.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_id', help='Server ID')
    parser.add_argument('--replication_factor', help='Replication factor')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    raft_config = IniConfig('src/configurations/config.ini')
    raft_servers_config = JsonConfig('src/configurations/servers.json').get_all_properties()

    server_id = args.server_id if args.server_id is not None else \
        raft_config.get_property('raft', 'server_id')
    replication_factor = args.replication_factor if args.replication_factor is not None else \
        raft_servers_config[server_id]['host']

    kv_server = KVServer(_id=int(server_id), _replication_factor=int(replication_factor))
    kv_server.run()
