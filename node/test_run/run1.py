from node.test_run.api_run_helper import RaftServerApp

if __name__ == "__main__":
    raft_server_id = 1
    uvicorn_host = "0.0.0.0"
    uvicorn_port = 8001

    app = RaftServerApp(raft_server_id, uvicorn_host, uvicorn_port, 'uncommitted_log_1.txt', 'committed_log_1.txt')
    app.start()
