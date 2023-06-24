import datetime
import sys

from prompt_toolkit import PromptSession

from src.cli.cli_commands import run_htop, basic_commands, show_help, show_wellcome_screen, execute_command
from src.raft_node.api_helper import ApiHelper, get_server_state


def _exit():
    print("Exiting Raft CLI. Bye!")
    sys.exit(0)


class RaftCli:

    def __init__(self):
        self.api_username = None
        self.api_password = None
        self.host = None
        self.port = None
        self.session = PromptSession(completer=basic_commands)
        self.basic_commands = None
        self.api_helper = None
        self.is_connected = False

    def login(self):
        login_true = False
        first_time = True
        response = None
        while not login_true:
            if first_time:
                print("\nPlease provide the following information to continue.\n")
            else:
                print(response['message'])
            self.host = self.session.prompt("Hostname [127.0.0.1]: ", is_password=False)
            if not self.host:
                self.host = '127.0.0.1'
            self.port = self.session.prompt("Port [8001]: ", is_password=False)
            if not self.port:
                self.port = '8001'
            self.api_username = self.session.prompt("API Username [admin]: ", is_password=False)
            if not self.api_username:
                self.api_username = 'admin'
            self.api_password = self.session.prompt("API Password [admin]: ", is_password=True)
            if not self.api_password:
                self.api_password = 'admin'
            self.api_helper = ApiHelper(self.host, self.port, self.api_username, self.api_password)
            response = self.api_helper.login()
            login_true = response['login']
            if login_true:
                self.is_connected = True
            first_time = False

            # Clear input lines
            for i in range(7):
                sys.stdout.write("\033[F")  # Move cursor up one line
                sys.stdout.write("\033[K")  # Clear line

        print(f"\nLogin successful.!")

    def logout(self):
        self.api_username = None
        self.api_password = None
        self.host = None
        self.port = None
        self.is_connected = False

    def start_cl(self):
        response = self.api_helper.get_servers()
        for server_id, info in response['api_servers'].items():
            self.api_helper.start_stop_server(info['host'], info['port'], 'start_server')

    def stop_cl(self):
        response = self.api_helper.get_servers()
        for server_id, info in response['api_servers'].items():
            self.api_helper.start_stop_server(info['host'], info['port'], 'stop_server')

    def _get_state(self):
        # response = self.api_helper.get_state()
        response = self.api_helper.get_servers()
        for server_id, info in response['api_servers'].items():
            state_response = get_server_state(info['host'], info['port'], 'admin', 'admin')
            if state_response['status'] == 'OK':
                if server_id == state_response['leader_id']:
                    print(f"[+] Server {server_id} [ Leader ]: {info} (online"
                          f" - {'running' if state_response['is_running'] else 'not running'})")
                else:
                    print(f"[*] Server {server_id} [Follower]: {info} (online"
                          f" - {'running' if state_response['is_running'] else 'not running'})")
            else:
                print(f"[-] Server {server_id} [Follower]: {info} (offline - not running)")

    def process_user_input(self, user_input):
        # only allow login and exit commands if self.is_connected is False
        allowed_commands = ["login", "exit", "clear", "help"]
        if not self.is_connected:
            if user_input not in allowed_commands:
                print("You must first login to the cluster. Type 'login' to continue.")
                return
        switcher = {
            "time": lambda: print("Current time:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "hello": lambda: print("Hello, World!"),
            "status": run_htop,
            "login": self.login,
            "help": show_help,
            "clear": lambda: print(execute_command(user_input)),
            "exit": lambda: _exit(),
            "logout": self.logout,
            "get_state": lambda: self._get_state(),
            "start_cl": lambda: self.start_cl(),
            "stop_cl": lambda: self.stop_cl(),
            "": lambda: None
        }

        func = switcher.get(user_input, lambda: print("Unknown command:", user_input))
        func()

    def run(self):
        while True:
            try:
                if not self.is_connected:
                    user_input = self.session.prompt("\n> ", is_password=False)
                else:
                    user_input = self.session.prompt(f"\n{self.api_username}@{self.host}> ", is_password=False)
                self.process_user_input(user_input)
            except KeyboardInterrupt:
                # Handle Ctrl+C
                break
            except EOFError:
                # Handle Ctrl+D
                break


if __name__ == "__main__":
    raft_cli = RaftCli()
    show_wellcome_screen()
    raft_cli.run()
