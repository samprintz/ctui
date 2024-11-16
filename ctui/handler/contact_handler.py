class ContactHandler:
    def __init__(self, core):
        self.core = core

    def has_details(self, contact):
        return self.core.rdfstore.has_attributes(contact) or \
            self.core.textfilestore.has_gifts(contact.get_id()) or \
            self.core.textfilestore.has_notes(contact.get_id())

    def load_details(self, contact):
        contact.attributes = self.core.rdfstore.get_attributes(contact)
        contact.gifts = self.core.textfilestore.get_gifts(contact.get_id())
        contact.notes = self.core.textfilestore.get_notes(contact.get_id())
