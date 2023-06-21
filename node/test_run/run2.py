from node.test_run.api_run_helper import RaftServerApp

if __name__ == "__main__":
    raft_server_id = 2
    uvicorn_host = "0.0.0.0"
    uvicorn_port = 8002

    app = RaftServerApp(raft_server_id, uvicorn_host, uvicorn_port, 'mongodb://localhost:27017',
                        'raft', 'log_2')
    app.start()
