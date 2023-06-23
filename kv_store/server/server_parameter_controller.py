class ParametersController:
    def __init__(self):
        self.ip_address = None
        self.port = None

    def parse_parameters(self, args):
        if not self._has_correct_num_of_parameters(args):
            raise ValueError(f"Error: Incorrect number of parameters. Expected 4, received {len(args)}.")

        self._assign_parameters(args)

    @staticmethod
    def _has_correct_num_of_parameters(args):
        return len(args) == 4

    def _assign_parameters(self, args):
        for i in range(0, len(args), 2):
            flag = args[i]
            value = args[i + 1]

            if flag == "-a":
                self.ip_address = value
            elif flag == "-p":
                try:
                    self.port = int(value)
                except ValueError:
                    raise ValueError(f"Error: Invalid port value '{value}'. Port must be an integer.")
            else:
                raise ValueError(f"Error: Unknown parameter flag '{flag}'.")

    def get_ip_address(self):
        return self.ip_address

    def get_port(self):
        return self.port
