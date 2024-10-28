class MemoryStore:
    """
    Store for in-memory information. Used when displaying encrypted notes. This
    allows to show encrypted information for multiple contacts that is deleted
    when closing the program for security reasons.
    """

    def __init__(self):
        self.notes = {}

    def has_notes(self, contact):
        if contact.name not in self.notes:
            return False
        return len(self.notes[contact.name]) > 0

    def get_notes(self, contact):
        if contact.name not in self.notes:
            return False
        return self.notes[contact.name]

    def has_note(self, contact, note_id):
        return contact.name in self.notes and \
            note_id in self.notes[contact.name]

    def add_note(self, contact, note):
        if contact.name not in self.notes:
            self.notes[contact.name] = {}
        self.notes[contact.name][note.note_id] = note
        return True

    def get_note(self, contact, note_id):
        if not self.has_note(contact, note_id):
            return None
        else:
            return self.notes[contact.name][note_id]

    def delete_note(self, contact, note_id):
        if self.has_note(contact, note_id):
            del self.notes[contact.name][note_id]

    def delete_all_notes(self, contact):
        if self.has_notes(contact):
            del self.notes[contact.name]
