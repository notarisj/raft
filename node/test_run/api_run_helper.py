import threading
import uvicorn

from node.raft_server import RaftServer
from fastapi import FastAPI


class RaftServerApp:
    def __init__(self, raft_server_id, uvicorn_host, uvicorn_port):
        self.raft_server_id = raft_server_id
        self.uvicorn_host = uvicorn_host
        self.uvicorn_port = uvicorn_port

    def create_app(self):
        app = FastAPI()

        @app.post("/append_entries")
        def append_entries(_append_entries: dict):
            entries = _append_entries.get("entries", [])
            self.server.send_append_entries_to_server_multicast(entries)
            return {"message": "Log entries appended"}

        @app.get("/get_log")
        def get_log():
            return self.server.log.entries

        return app

    def start(self):
        servers = {1: {'host': 'localhost', 'port': 5001},
                   2: {'host': 'localhost', 'port': 5002},
                   3: {'host': 'localhost', 'port': 5003}}

        self.server = RaftServer(self.raft_server_id, servers)
        app = self.create_app()
        uvicorn.run(app, host=self.uvicorn_host, port=self.uvicorn_port)
