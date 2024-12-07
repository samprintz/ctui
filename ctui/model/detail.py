class Detail:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'Detail({self.name})'

    def __eq__(self, other):
        return self.name == other.name
