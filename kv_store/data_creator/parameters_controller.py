class ParametersController:
    def __init__(self):
        self.key_file_path = ""
        self.num_of_lines = 0
        self.max_nesting_level = 0
        self.max_key_num_of_value = 0
        self.max_string_length = 0

    def read_parameters(self, args):
        if len(args) != 11:
            raise ValueError("Error: Incorrect number of parameters. Expected 10, got {}".format(len(args)))
        self.assign_parameters(args)

    def assign_parameters(self, args):
        for i in range(1, len(args), 2):
            flag = args[i]
            value = args[i + 1]
            try:
                if flag == "-k":
                    self.key_file_path = value
                elif flag == "-n":
                    self.num_of_lines = int(value)
                elif flag == "-d":
                    self.max_nesting_level = int(value)
                elif flag == "-m":
                    self.max_key_num_of_value = int(value)
                elif flag == "-l":
                    self.max_string_length = int(value)
                else:
                    raise ValueError("Error: Invalid parameter flag: {}".format(flag))
            except ValueError:
                raise ValueError("Error: Failed to convert value '{}' for parameter flag '{}' to an integer".format(value, flag))

    def get_key_file_path(self):
        return self.key_file_path

    def get_num_of_lines(self):
        return self.num_of_lines

    def get_max_nesting_level(self):
        return self.max_nesting_level

    def get_max_key_num_of_value(self):
        return self.max_key_num_of_value

    def set_max_key_num_of_value(self, new_size):
        if new_size < self.max_key_num_of_value:
            print("Warning: The max number of keys inside values must not be greater than the number of keys. "
                  "Changing value from {} to {}".format(self.max_key_num_of_value, new_size))
            self.max_key_num_of_value = new_size

    def get_max_string_length(self):
        return self.max_string_length
