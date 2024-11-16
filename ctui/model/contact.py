class Contact:

    def __init__(self, name, attributes=None, gifts=None, notes=None):
        self.name = name
        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_id(self):
        return self.name.replace(' ', '_')
