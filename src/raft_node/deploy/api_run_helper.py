import uvicorn

from src.configurations import JsonConfig
from src.raft_node.api_helper import api_post_request
from src.raft_node.raft_server import RaftServer
from fastapi import FastAPI


def split_dictionary(original_dict):
    result_dict_raft = {}
    result_dict_api = {}

    for key, value in original_dict.items():
        new_key = int(key)
        host = value['host']

        raft_dict = {'host': host, 'port': value['raft_port']}
        result_dict_raft[new_key] = raft_dict

        api_dict = {'host': host, 'port': value['api_port']}
        result_dict_api[new_key] = api_dict

    return result_dict_raft, result_dict_api


class RaftServerApp:

    def __init__(self, raft_server_id, uvicorn_host, uvicorn_port, database_uri, database_name, collection_name):
        self.server = None
        self.raft_server_id = raft_server_id
        self.uvicorn_host = uvicorn_host
        self.uvicorn_port = uvicorn_port
        self.database_uri = database_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.raft_config = JsonConfig('src/raft_node/deploy/raft_servers.json')
        self.servers, self.api_servers = split_dictionary(self.raft_config.config)

    def create_app(self):
        app = FastAPI()

        @app.post("/append_entries")
        def append_entries(_append_entries: dict):
            if self.server.server_id != self.server.leader_id:
                api_post_request(f"http://0.0.0.0:{self.api_servers[self.server.leader_id]['port']}/append_entries",
                                 _append_entries)
                return {"message": f"Forwarded to leader server {self.server.leader_id}"}
            else:
                commands = _append_entries.get("commands", [])
                self.server.append_entries_to_leader(commands)
                return {"message": "Log entries appended"}

        @app.get("/get_log")
        def get_log():
            return self.server.log.entries

        return app

    def start(self):
        self.server = RaftServer(self.raft_server_id, self.servers,
                                 self.database_uri, self.database_name, self.collection_name)
        app = self.create_app()
        uvicorn.run(app, host=self.uvicorn_host, port=int(self.uvicorn_port))
