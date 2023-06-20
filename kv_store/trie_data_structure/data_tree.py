class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.children = []


class Tree:
    def __init__(self):
        self.root = Node("root", None)

    def insert(self, json_obj):
        self.build_tree(self.root, json_obj)

    def build_tree(self, node, json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                child_node = Node(key, None)  # Set value as None initially
                node.children.append(child_node)
                self.build_tree(child_node, value)
        else:
            node.value = json_obj  # Store the value when it is not a dictionary

    def print_tree(self, node=None, indent=""):
        if node is None:
            node = self.root
        print(indent + node.key + ": " + str(node.value))
        for child in node.children:
            self.print_tree(child, indent + "  ")

    def search(self, key_path, node=None, visited_keys=None):
        if node is None:
            node = self.root

        if visited_keys is None:
            visited_keys = {}

        keys = key_path.split('.')
        current_key = keys[0]
        remaining_keys = '.'.join(keys[1:])

        if current_key == "":
            return self.get_value(node, visited_keys)

        for child in node.children:
            if child.key == current_key:
                visited_keys[child.key] = True
                result = self.search(remaining_keys, child, visited_keys.copy())  # Use a copy of visited_keys
                if result is not None:
                    return result

        return None

    def delete(self, top_key):
        self.delete_node(self.root, top_key)

    def delete_node(self, node, key):
        for child in node.children:
            if child.key == key:
                node.children.remove(child)
                return

            self.delete_node(child, key)

    def get_value(self, node, visited_keys):
        if len(node.children) > 0:
            value = {}
            for child in node.children:
                child_value = self.get_value(child, visited_keys)
                if child_value is not None:
                    value.update(child_value)
            return {node.key: value} if value else {node.key: {}}  # Return an empty dictionary if value is None
        else:
            return {node.key: node.value} if node.value is not None else {
                node.key: {}}  # Return an empty dictionary if value is None
