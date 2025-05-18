class DiscordClient:
    # Class attribute shared by all instances
    class_attribute = "I belong to the class"

    # Constructor method (initializer)
    def __init__(self, name, value):
        # Instance attributes unique to each instance
        self.name = name
        self.value = value

    # Instance method
    def display_info(self):
        return f"Name: {self.name}, Value: {self.value}"

    # Another instance method
    def modify_value(self, new_value):
        self.value = new_value
        return f"Value updated to {self.value}"

    # Class method (operates on the class, not instances)
    @classmethod
    def from_string(cls, string_data):
        name, value = string_data.split(',')
        return cls(name, int(value))

    # Static method (doesn't access class or instance variables)
    @staticmethod
    def helper_function(x):
        return x * 2
