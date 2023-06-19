import uvicorn

from node.api_helper import api_post_request
from node.raft_server import RaftServer
from fastapi import FastAPI


class RaftServerApp:
    def __init__(self, raft_server_id, uvicorn_host, uvicorn_port, uncommitted_log_file_path=None,
                 committed_log_file_path=None):
        self.server = None
        self.raft_server_id = raft_server_id
        self.uvicorn_host = uvicorn_host
        self.uvicorn_port = uvicorn_port
        self.uncommitted_log_file_path = uncommitted_log_file_path
        self.committed_log_file_path = committed_log_file_path
        self.servers = {1: {'host': 'localhost', 'port': 5001},
                        2: {'host': 'localhost', 'port': 5002},
                        3: {'host': 'localhost', 'port': 5003}}
        self.api_servers = {1: {'host': 'localhost', 'port': 8001},
                            2: {'host': 'localhost', 'port': 8002},
                            3: {'host': 'localhost', 'port': 8003}}

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
                self.server.send_append_entries_to_server_multicast(commands)
                return {"message": "Log entries appended"}

        @app.get("/get_log")
        def get_log():
            return self.server.log.entries

        return app

    def start(self):
        self.server = RaftServer(self.raft_server_id, self.servers,
                                 self.uncommitted_log_file_path,
                                 self.committed_log_file_path)
        app = self.create_app()
        uvicorn.run(app, host=self.uvicorn_host, port=self.uvicorn_port)
