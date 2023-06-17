from node.test_run.api_run_helper import RaftServerApp

if __name__ == "__main__":
    raft_server_id = 3
    uvicorn_host = "0.0.0.0"
    uvicorn_port = 8003

    app = RaftServerApp(raft_server_id, uvicorn_host, uvicorn_port)
    app.start()
