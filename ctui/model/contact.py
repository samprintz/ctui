class Contact:

    def __init__(self, name, attributes=None, gifts=None, notes=None):
        self.name = name
        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_id(self):
        return Contact.name_to_id()

    def __str__(self):
        return f'Contact({self.name})'

    @classmethod
    def id_to_name(cls, contact_id):
        return contact_id.replace('_', ' ')

    @classmethod
    def name_to_id(cls, name):
        return name.replace(' ', '_')
