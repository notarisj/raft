import argparse
from src.configurations.read_config import IniConfig, JsonConfig
from src.kv_store.server import KVServer


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_id', help='Server ID')
    parser.add_argument('--replication_factor', help='Replication factor')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    raft_config = IniConfig('src/raft_node/deploy/config.ini')
    raft_servers_config = JsonConfig('src/raft_node/deploy/servers.json').config

    server_id = args.server_id if args.server_id is not None else \
        raft_config.get_property('raft', 'server_id')
    replication_factor = args.replication_factor if args.replication_factor is not None else \
        raft_servers_config[server_id]['host']

    kv_server = KVServer(_id=int(server_id), _replication_factor=int(replication_factor))
    kv_server.run()
