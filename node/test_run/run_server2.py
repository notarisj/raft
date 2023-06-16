import threading
import uvicorn

from node.raft_server import RaftServer
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


class LogEntryModel(BaseModel):
    term: int
    command: str


class AppendEntriesModel(BaseModel):
    entries: List[LogEntryModel]


app = FastAPI()

global server


# Assuming you have a global instance of the RaftServer named raft_server
@app.post("/append_entries")
def append_entries(_append_entries: AppendEntriesModel):
    global server
    server.send_append_entries_to_server_multicast(_append_entries.entries)
    return {"message": "Log entries appended"}


@app.get("/get_log")
def get_log():
    global server
    return server.log.entries


def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    servers = {1: {'host': 'localhost', 'port': 5001},
               2: {'host': 'localhost', 'port': 5002},
               3: {'host': 'localhost', 'port': 5003}}

    # Initialize the server object before running FastAPI
    server = RaftServer(2, servers)
    uvicorn_thread = threading.Thread(target=run_uvicorn)
    uvicorn_thread.start()
    server.run()
