class Attribute:

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __lt__(self, other):
        return (self.key, self.value) < (other.key, other.value)

    def __str__(self):
        return f'Attribute({self.key}, {self.value})'
