import os
import random


class CreateValues:
    def __init__(self, data_map, parameters_controller):
        self.top_lvl_key_prefix = "key"
        self.created_file_path = "/home/giannis-pc/Desktop/raft/kv_store/resources/dataToIndex.txt"
        self.data_map = data_map
        self.parameters_controller = parameters_controller
        self.nested_value_possibility = 0.25

    def create_data(self):
        lines = []
        for i in range(self.parameters_controller.get_num_of_lines()):
            line = self.generate_line(i)
            lines.append(line)
        data = "\n".join(lines)
        self.write_to_file(data)

    def generate_line(self, index):
        top_level_key = "{}{}".format(self.top_lvl_key_prefix, index + 1)
        value = self.generate_value(self.parameters_controller.get_max_nesting_level())
        line = '{{ "{}" : {} }}'.format(top_level_key, value)
        return line

    def generate_value(self, nesting_level):
        value_list = []
        num_keys_of_current_level = random.randint(0, self.parameters_controller.get_max_key_num_of_value())
        used_keys = []
        for _ in range(num_keys_of_current_level):
            new_key = self.get_accepted_key(list(self.data_map.keys()), used_keys)
            used_keys.append(new_key)
            key_value_pair = self.generate_key_value_pair(new_key, nesting_level)
            value_list.append(key_value_pair)
        value = " , ".join(value_list)
        return "{{ {} }}".format(value)

    def generate_key_value_pair(self, key, nesting_level):
        if nesting_level > 0 and self.add_nested_value():
            nested_value = self.generate_value(nesting_level - 1)
            return '"{}" : {}'.format(key, nested_value)
        else:
            value_type = self.data_map.get(key)
            if value_type == "int":
                return '"{}" : {}'.format(key, random.randint(0, 100))
            elif value_type == "float":
                return '"{}" : {}'.format(key, random.uniform(0, 100))
            elif value_type == "string":
                max_length = self.parameters_controller.get_max_string_length()
                random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=max_length))
                return '"{}" : "{}"'.format(key, random_string)
            else:
                print("Warning: Invalid type '{}' for key '{}'. It should be 'int', 'float', or 'string'. "
                      "Assuming 'int'.".format(value_type, key))
                return '"{}" : {}'.format(key, random.randint(0, 100))

    def add_nested_value(self):
        return random.random() <= self.nested_value_possibility

    @staticmethod
    def get_accepted_key(key_set, used_keys):
        available_keys = [k for k in key_set if k not in used_keys]
        if not available_keys:
            raise ValueError("Error: No available keys to choose from.")
        return random.choice(available_keys)

    def write_to_file(self, data):
        directory = os.path.dirname(self.created_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            with open(self.created_file_path, "w") as file:
                file.write(data)
            print("Successfully wrote to the file.")
        except IOError as e:
            print("Error: Failed to write to the file '{}'. {}".format(self.created_file_path, str(e)))
            exit(-1)
