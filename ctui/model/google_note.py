class GoogleNote:

    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        return self.content == other.content
