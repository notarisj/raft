import argparse
import subprocess
from tabulate import tabulate

from prompt_toolkit.completion import WordCompleter

from src.raft_node.api_helper import get_server_state

basic_commands = WordCompleter(["start_cl", "stop_cl", "get_state", "edit_config", "login", "exit", "help", "clear"])


def show_wellcome_screen():
    print("\n=================================================================")
    print("==================== Raft CLI Manager (v1.0) ====================")
    print("=================================================================")
    print("\nYou must first login to the cluster. Type 'login' to continue.")


def execute_command(command):
    """
    Execute a command in the shell and return the output.
    """
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _output, _ = process.communicate()
    return _output.decode().strip()


def start_cl(api_helper):
    response = api_helper.get_servers()
    for server_id, info in response['api_servers'].items():
        response = api_helper.start_stop_server(info['host'], info['port'], 'start_server')
        if response is not None:
            print(f"Server {server_id}: {response.json()}")
        else:
            print(f"Server {server_id} failed to stop.")


def stop_cl(api_helper):
    response = api_helper.get_servers()
    for server_id, info in response['api_servers'].items():
        response = api_helper.start_stop_server(info['host'], info['port'], 'stop_server')
        if response is not None:
            print(f"Server {server_id}: {response.json()}")
        else:
            print(f"Server {server_id} failed to stop.")


def get_cluster_state(api_helper):
    response = api_helper.get_servers()
    headers = ["Node ID", "Status", "Running", "Role", "Host", "Port"]
    table = []
    for server_id, info in response['api_servers'].items():
        state_response = get_server_state(info['host'], info['port'], 'admin', 'admin')
        if state_response['status'] == 'ERROR':
            is_running = 'not running'
        else:
            is_running = 'running' if state_response['is_running'] else 'not running'
        if state_response['status'] == 'OK':
            if server_id == state_response['leader_id']:
                table.append([server_id, '\033[32m\u25CF\033[0m online', is_running,
                              state_response['state'], info['host'], info["port"]])
            else:
                table.append([server_id, '\033[32m\u25CF\033[0m online', is_running,
                              state_response['state'], info['host'], info["port"]])
        else:
            table.append([server_id, '\033[31m\u25CF\033[0m offline', is_running,
                          '-', info['host'], info["port"]])

    # Set align='left' for all columns
    align_options = ['center'] * len(headers)
    table_formatted = tabulate(table, headers, tablefmt="grid", colalign=align_options)
    print(table_formatted)


def show_help():
    parser = argparse.ArgumentParser(description='CLI Tool Help')

    # Define commands and their descriptions
    commands = {
        'start-cl': 'Start the cluster',
        'stop-cl': 'Stop the cluster',
        'get_state': 'Get the state of the cluster',
        'edit_config': 'Edit the configuration file. Add, remove and update nodes.',
        'login': 'Login to the cluster',
        'exit': 'Exit the CLI',
        'clear': 'Clear the screen'
    }

    # Add commands as subparsers
    subparsers = parser.add_subparsers(title='Commands')

    for command, description in commands.items():
        subparsers.add_parser(command, help=description)

    parser.print_help()
