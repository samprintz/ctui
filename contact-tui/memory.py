"""
Store for in-memory information. Used when displaying encrypted notes. This
allows to show encrypted information for multiple contacts that is deleted
when closing the program for security reasons.
"""
class MemoryStore:

    def __init__(self):
        self.notes = {}


    def get_notes(self, contact):
        return self.notes[contact.name]


    def contains_note(self, contact, date):
        return contact.name in self.notes is not None and \
                date in self.notes[contact.name] is not None


    def add_note(self, contact, note):
        if contact.name not in self.notes:
            self.notes[contact.name] = {}
        self.notes[contact.name][note.date] = note
        return True


    def get_note(self, contact, date):
        if not self.contains_note(contact, date):
            return None
        else:
            return self.notes[contact.name][date]

    def delete_note(self, contact, date):
        if self.contains_note(contact, date):
            del self.notes[contact.name][date]
