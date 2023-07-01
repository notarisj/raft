import json

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style
from tabulate import tabulate

from src.configuration_reader import JsonConfig
from src.rpc import RPCClient

servers = JsonConfig('src/configurations/servers.json')


def save_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


class NodeEditor:

    def __init__(self):
        print("Initializing Node Editor...")
        self.kv_store_rpc_clients = {server_id: RPCClient(host=server['host'], port=server['kv_port'])
                                     for server_id, server in servers.config.items()}

    def edit_json_file(self, file_path, api_helper):
        """
        Interactive editor for the servers.json file

        Args:
            file_path (str): Path to the servers.json file
            api_helper (ApiHelper): ApiHelper object for making API calls
        """
        with open(file_path, 'r') as file:
            data = json.load(file)

        session = PromptSession()
        style = Style.from_dict({
            'prompt': 'bold',
            'output': '#ansibrightgreen',
        })

        # Interactive editing loop
        while True:
            print("Raft Nodes:")
            headers = ["Node ID", "Host", "Raft Port", "API Port", "KV Port"]
            table = []
            for node_id, node_data in data.items():
                table.append([node_id, node_data['host'], node_data['raft_port'], node_data['api_port'],
                              node_data['kv_port']])

            align_options = ['center'] * len(headers)
            table_formatted = tabulate(table, headers, tablefmt="grid", colalign=align_options)
            print(table_formatted)

            print("\nEnter the operation to perform:")
            print("1. Add a new node")
            print("2. Edit an existing node")
            print("3. Delete an existing node")
            print("4. Quit")
            user_input = session.prompt('\n> ', style=style)

            if user_input == '1':
                new_host = session.prompt('Enter host: ', style=style)
                new_raft_port = int(session.prompt('Enter raft_port: ', style=style))
                new_api_port = int(session.prompt('Enter api_port: ', style=style))
                new_kv_port = int(session.prompt('Enter kv_port: ', style=style))
                new_node = {
                    'host': new_host,
                    'raft_port': new_raft_port,
                    'api_port': new_api_port,
                    'kv_port': new_kv_port
                }
                node_id = str(int(max(data, key=lambda x: int(x))) + 1)
                data[node_id] = new_node
                payload = {
                    "id": node_id,
                    'host': new_host,
                    'raft_port': new_raft_port,
                    'api_port': new_api_port,
                    'kv_port': new_kv_port
                }
                self.push_update(api_helper, payload, 'add_node')
                self.kv_store_rpc_clients[node_id] = RPCClient(host=new_host, port=new_kv_port)
                print(f"\nNode {node_id} has been added.")
                save_json_file(file_path, data)
            elif user_input == '2':
                node_id = session.prompt('Enter the node ID to edit: ', style=style)
                if node_id in data:
                    node_data = data[node_id]
                    new_host = session.prompt('Enter new host: ', default=node_data['host'], style=style)
                    new_raft_port = int(session.prompt('Enter new raft_port: ',
                                                       default=str(node_data['raft_port']), style=style))
                    new_api_port = int(session.prompt('Enter new api_port: ',
                                                      default=str(node_data['api_port']), style=style))
                    new_kv_port = int(session.prompt('Enter new kv_port: ',
                                                     default=str(node_data['kv_port']), style=style))
                    data[node_id] = {
                        'host': new_host,
                        'raft_port': new_raft_port,
                        'api_port': new_api_port,
                        'kv_port': new_kv_port
                    }
                    payload = {
                        "id": node_id,
                        'host': new_host,
                        'raft_port': new_raft_port,
                        'api_port': new_api_port,
                        'kv_port': new_kv_port
                    }
                    self.push_update(api_helper, payload, 'update_node')
                    # TODO: Implement UPDATE NODE
                    print(f"\nNode {node_id} has been updated.")
                    save_json_file(file_path, data)
                else:
                    print(f"Node {node_id} does not exist in the JSON data.")
            elif user_input == '3':
                node_id = session.prompt('Enter the node ID to delete: ', style=style)
                if node_id in data:
                    del data[node_id]
                    del self.kv_store_rpc_clients[node_id]
                    self.push_update(api_helper, node_id, 'delete_node')
                    print(f"\nNode {node_id} has been deleted.")
                    save_json_file(file_path, data)
                else:
                    print(f"Node {node_id} does not exist in the JSON data.")
            elif user_input == '4':
                break
            else:
                print("Invalid input. Please enter a valid operation.")

    def push_update(self, api_helper, payload, action):
        """
        Pushes an update to the raft servers and kv store servers

        Args:
            api_helper (ApiHelper): ApiHelper object for making API calls
            payload (dict): Payload to send to the servers
            action (str): Action to perform on the servers (add_node, update_node, delete_node)
        """
        response = api_helper.get_servers()

        # Update raft server
        for server_id, info in response['api_servers'].items():
            api_helper.node_actions(info['host'], info['port'], payload, action)

        # Update kv store servers
        for key, rpc_client in self.kv_store_rpc_clients.items():
            print(f"Sending {action} to server {key}")
            _payload = {"command": action,
                        "payload": payload}
            rpc_client.call('update_raft_config', json.dumps(_payload))
