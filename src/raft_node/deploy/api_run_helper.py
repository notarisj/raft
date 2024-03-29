import concurrent.futures

import uvicorn
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse

from src.configuration_reader import JsonConfig, IniConfig
from src.raft_node.api_helper import api_post_request
from src.raft_node.raft_server import RaftServer, RaftState
from fastapi import FastAPI, Depends, HTTPException, status, Request

raft_config = IniConfig('src/configurations/config.ini')


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


def get_current_username(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    Validates the provided username and password against the configured credentials.

    Args:
        credentials: The HTTP basic authentication credentials.

    Returns:
        The username if the credentials are correct.

    Raises:
        HTTPException with status code 401 if the credentials are incorrect.
    """
    correct_username = raft_config.get_property('API', 'username')
    correct_password = raft_config.get_property('API', 'password')
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class RaftServerApp:

    def __init__(self, raft_server_id, uvicorn_host, uvicorn_port, database_uri, database_name, collection_name,
                 ssl_cert_file, ssl_key_file):
        self.kv_server = None
        self.server = None
        self.raft_server_id = raft_server_id
        self.uvicorn_host = uvicorn_host
        self.uvicorn_port = uvicorn_port
        self.database_uri = database_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.raft_config = JsonConfig('src/configurations/servers.json')
        self.servers, self.api_servers = split_dictionary(self.raft_config.config)
        self.server_executor = concurrent.futures.ThreadPoolExecutor()
        self.ssl_cert_file = ssl_cert_file
        self.ssl_key_file = ssl_key_file

    def create_app(self):
        app = FastAPI()

        @app.middleware("http")
        async def force_https(request: Request, call_next):
            """Middleware to force HTTPS redirect"""
            if request.url.scheme == "http":
                https_url = request.url.replace(scheme="https")
                response = RedirectResponse(url=https_url)
                return response
            return await call_next(request)

        @app.post("/append_entries")
        def append_entries(_append_entries: dict, _: str = Depends(get_current_username)):
            if self.server.server_id != self.server.leader_id:
                api_post_request(f"https://127.0.0.1:{self.api_servers[self.server.leader_id]['port']}/append_entries",
                                 _append_entries)
                return {"message": f"Forwarded to leader server {self.server.leader_id}"}
            else:
                # commands = _append_entries.get("commands", [])
                self.server.append_entries_to_leader(_append_entries)
                return {"message": "Log entries appended"}

        @app.get("/get_log")
        def get_log(_: str = Depends(get_current_username)):
            return self.server.log.entries

        @app.get("/authenticate")
        async def read_protected_endpoint(_: str = Depends(get_current_username)):
            return {'status': 'OK'}

        @app.post("/add_node")
        async def _add_node(server: dict, _: str = Depends(get_current_username)):
            self.server.add_node(int(server['id']), server['host'], server['raft_port'])
            entry = {
                'host': server['host'],
                'raft_port': server['raft_port'],
                'api_port': server['api_port'],
                'kv_port': server['kv_port']
            }
            self.raft_config.config[server['id']] = entry
            self.raft_config.save()
            self.api_servers[int(server['id'])] = {'host': server['host'], 'port': server['api_port']}
            return {'status': 'OK'}

        @app.post("/update_node")
        async def _update_node(server: dict, _: str = Depends(get_current_username)):
            self.server.update_node(int(server['id']), server['host'], server['raft_port'])
            entry = {
                'host': server['host'],
                'raft_port': server['raft_port'],
                'api_port': server['api_port'],
                'kv_port': server['kv_port']
            }
            self.raft_config.config[server['id']] = entry
            self.raft_config.save()
            self.api_servers[int(server['id'])] = {'host': server['host'], 'port': server['api_port']}
            return {'status': 'OK'}

        @app.post("/delete_node/{server_id}")
        async def _delete_node(server_id: int, _: str = Depends(get_current_username)):
            if server_id == self.server.server_id:
                self.server.is_running = False
                self.server.rpc_server.stop()
            self.server.delete_node(int(server_id))
            del self.raft_config.config[str(server_id)]
            self.raft_config.save()
            del self.api_servers[int(server_id)]
            return {'status': 'OK'}

        @app.get("/get_servers")
        def get_state(_: str = Depends(get_current_username)):
            return {"status": 'OK', "api_servers": self.api_servers, "raft_servers": self.servers}

        @app.get("/get_state")
        def get_state(_: str = Depends(get_current_username)):
            return {"status": "OK",
                    "leader_id": str(self.server.leader_id),
                    "is_running": self.server.is_running,
                    "state": self.server.state.name,
                    "message": 'All OK'}

        @app.post("/start_server")
        def get_state(_: str = Depends(get_current_username)):
            if self.server.is_running:
                return {"status": 'OK', "message": "Server already running"}
            self.server.is_running = True
            self.server_executor.submit(self.server.run)
            return {"status": 'OK'}

        @app.post("/stop_server")
        def get_state(_: str = Depends(get_current_username)):
            if not self.server.is_running:
                return {"status": 'OK', "message": "Server already stopped"}
            self.server.is_running = False
            self.server.state = RaftState.FOLLOWER
            return {"status": 'OK'}

        return app

    def start(self):
        self.server = RaftServer(self.raft_server_id, self.servers, self.database_uri,
                                 self.database_name, self.collection_name)

        app = self.create_app()
        uvicorn.run(app, host=self.uvicorn_host, port=int(self.uvicorn_port),
                    ssl_keyfile=self.ssl_key_file, ssl_certfile=self.ssl_cert_file)
