import sys
import time
from parameters_controller import ParametersController
from kv_store.my_io.read_file import get_data_from_file
from create_values import CreateValues


if __name__ == "__main__":
    print(
        "Welcome to DataCreation! This program generates syntactically correct data that will be loaded to a key "
        "value database.")

    parameters_controller = ParametersController()
    parameters_controller.read_parameters(sys.argv)

    data_map = get_data_from_file(parameters_controller.get_key_file_path())
    parameters_controller.set_max_key_num_of_value(len(data_map))

    create_values = CreateValues(data_map, parameters_controller)
    start_time = time.time()
    create_values.create_data()
    end_time = time.time()
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    milliseconds = int((elapsed_time * 1000) % 1000)
    print(f"Data created after: {hours} hours {minutes} minutes {seconds} seconds {milliseconds} milliseconds")
