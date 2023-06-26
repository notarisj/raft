import argparse
import subprocess

from prompt_toolkit.completion import WordCompleter

basic_commands = WordCompleter(["PUT", "SEARCH", "DELETE", "clear", "exit", "help"])


def show_wellcome_screen():
    print("=================================================================")
    print("================= Key Value Store Client (v1.0) =================")
    print("=================================================================")


def execute_put(key, value):
    print(f"Implement here the PUT command with key: {key} and value: {value}")


def execute_search(key):
    print(f"Implement here the SEARCH command with key: {key}")


def execute_delete(key):
    print(f"Implement here the DELETE command with key: {key}")


def execute_command(command):
    """
    Execute a command in the shell and return the output.
    """
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _output, _ = process.communicate()
    return _output.decode().strip()


def show_help():
    parser = argparse.ArgumentParser(description='Key Value Client Tool Help')

    # Define commands and their descriptions
    commands = {
        'PUT': 'Inserts a new key (usage: PUT "key": "valid_json")',
        'SEARCH': 'Searches for a key (usage: SEARCH key.path.to.field1)',
        'DELETE': 'Deletes a key (usage: DELETE key)',
        'exit': 'Quit the client'
    }

    # Add commands as subparsers
    subparsers = parser.add_subparsers(title='Commands')

    for command, description in commands.items():
        subparsers.add_parser(command, help=description)

    parser.print_help()
