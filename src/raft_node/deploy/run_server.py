import argparse
from src.configurations.read_config import IniConfig, JsonConfig
from src.raft_node.deploy.api_run_helper import RaftServerApp


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_id', help='Server ID')
    parser.add_argument('--uvicorn_host', help='Uvicorn host')
    parser.add_argument('--uvicorn_port', help='Uvicorn port')
    parser.add_argument('--mongo_host', help='MongoDB host')
    parser.add_argument('--mongo_port', help='MongoDB port')
    parser.add_argument('--mongo_db_name', help='MongoDB database name')
    parser.add_argument('--mongo_collection_name', help='MongoDB collection name')
    parser.add_argument('--ssl_cert_file', help='SSL certificate file')
    parser.add_argument('--ssl_key_file', help='SSL key file')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    raft_config = IniConfig('src/raft_node/deploy/config.ini')
    raft_servers_config = JsonConfig('src/raft_node/deploy/raft_servers.json').config

    server_id = args.server_id if args.server_id is not None else \
        raft_config.get_property('raft', 'server_id')
    uvicorn_host = args.uvicorn_host if args.uvicorn_host is not None else \
        raft_servers_config[server_id]['host']
    uvicorn_port = args.uvicorn_port if args.uvicorn_port is not None else \
        raft_servers_config[server_id]['api_port']
    mongo_host = args.mongo_host if args.mongo_host is not None else \
        raft_config.get_property('MongoDB', 'mongo_host')
    mongo_port = args.mongo_port if args.mongo_port is not None else \
        raft_config.get_property('MongoDB', 'mongo_port')
    mongo_db_name = args.mongo_db_name if args.mongo_db_name is not None else \
        raft_config.get_property('MongoDB', 'mongo_db_name')
    mongo_collection_name = args.mongo_collection_name if args.mongo_collection_name is not None else \
        raft_config.get_property('MongoDB', 'mongo_collection_name')
    ssl_cert_file = args.ssl_cert_file if args.ssl_cert_file is not None else \
        raft_config.get_property('SSL', 'ssl_cert_file')
    ssl_key_file = args.ssl_cert_file if args.ssl_cert_file is not None else \
        raft_config.get_property('SSL', 'ssl_key_file')

    mongo_uri = f"mongodb://{mongo_host}:{mongo_port}"

    app = RaftServerApp(int(server_id), uvicorn_host, uvicorn_port, mongo_uri,
                        mongo_db_name, mongo_collection_name, ssl_cert_file, ssl_key_file)
    app.start()
