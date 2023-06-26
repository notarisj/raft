import json

from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style
from tabulate import tabulate


def save_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def edit_json_file(file_path, api_helper):
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
        headers = ["Node ID", "Host", "Raft Port", "API Port"]
        table = []
        for node_id, node_data in data.items():
            table.append([node_id, node_data['host'], node_data['raft_port'], node_data['api_port']])

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
            new_node = {
                'host': new_host,
                'raft_port': new_raft_port,
                'api_port': new_api_port
            }
            node_id = str(int(max(data, key=lambda x: int(x))) + 1)
            data[node_id] = new_node
            payload = {
                "id": node_id,
                'host': new_host,
                'raft_port': new_raft_port,
                'api_port': new_api_port
            }
            push_update(api_helper, payload, 'add_node')
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
                data[node_id] = {
                    'host': new_host,
                    'raft_port': new_raft_port,
                    'api_port': new_api_port
                }
                payload = {
                    "id": node_id,
                    'host': new_host,
                    'raft_port': new_raft_port,
                    'api_port': new_api_port
                }
                push_update(api_helper, payload, 'update_node')
                print(f"\nNode {node_id} has been updated.")
                save_json_file(file_path, data)
            else:
                print(f"Node {node_id} does not exist in the JSON data.")
        elif user_input == '3':
            node_id = session.prompt('Enter the node ID to delete: ', style=style)
            if node_id in data:
                del data[node_id]
                push_update(api_helper, node_id, 'delete_node')
                print(f"\nNode {node_id} has been deleted.")
                save_json_file(file_path, data)
            else:
                print(f"Node {node_id} does not exist in the JSON data.")
        elif user_input == '4':
            break
        else:
            print("Invalid input. Please enter a valid operation.")


def push_update(api_helper, payload, action):
    response = api_helper.get_servers()
    for server_id, info in response['api_servers'].items():
        api_helper.node_actions(info['host'], info['port'], payload, action)
