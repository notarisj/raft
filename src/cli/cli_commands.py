import argparse
import subprocess
import curses
import datetime

from prompt_toolkit.completion import WordCompleter

basic_commands = WordCompleter(["status", "list", "add", "remove", "restart", "start",
                                "stop", "start_cl", "stop_cl", "login", "exit", "help",
                                "clear", "get_state"])


def show_wellcome_screen():
    print("=================================================================")
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


def run_htop_mode(std_screen):
    std_screen.timeout(100)

    while True:
        std_screen.clear()
        height, width = std_screen.getmaxyx()
        std_screen.addstr(0, 0, f"HTOP Mode {datetime.datetime.now()}")
        std_screen.addstr(1, 0, "------------------------------------------------------------------")
        std_screen.addstr(2, 0, "Server 1 - [Leader]")
        std_screen.addstr(3, 0, "Server 2 - [Follower]")
        std_screen.addstr(4, 0, "Server 3 - [Follower]")
        std_screen.addstr(5, 0, "Server 4 - [Follower]")
        std_screen.addstr(6, 0, "Server 5 - [Follower]")
        std_screen.addstr(7, 0, "------------------------------------------------------------------")
        std_screen.addstr(height - 1, 0, "Press 'q' to exit HTOP mode.")

        std_screen.refresh()

        key = std_screen.getch()
        if key == ord('q'):
            break


def show_help():
    parser = argparse.ArgumentParser(description='CLI Tool Help')

    # Define commands and their descriptions
    commands = {
        'status': 'Displays the current status of the cluster',
        'list': 'Shows all the nodes in the cluster',
        'add': 'Adds a new node to the cluster',
        'remove': 'Remove a node from the cluster (usage: remove <node_id>)',
        'restart': 'Restart a node (usage: restart <node_id>)',
        'start': 'Start a node (usage: start <node_id>)',
        'stop': 'Stop a node (usage: stop <node_id>)',
        'start-cl': 'Start the cluster',
        'stop-cl': 'Stop the cluster',
        'login': 'Login to the cluster',
        'exit': 'Exit the CLI'
    }

    # Add commands as subparsers
    subparsers = parser.add_subparsers(title='Commands')

    for command, description in commands.items():
        subparsers.add_parser(command, help=description)

    parser.print_help()


def run_htop():
    curses.wrapper(run_htop_mode)
