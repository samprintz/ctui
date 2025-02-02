class MemoryStore:
    """
    Store for in-memory information. Used when displaying encrypted notes. This
    allows to show encrypted information for multiple contacts that is deleted
    when closing the program for security reasons.
    """

    def __init__(self):
        self.notes = {}

    def has_notes(self, contact_id):
        if contact_id not in self.notes:
            return False
        return len(self.notes[contact_id].keys()) > 0

    def get_notes(self, contact_id):
        if contact_id not in self.notes:
            return []
        return list(self.notes[contact_id].values())

    def has_note(self, contact_id, note_id):
        return contact_id in self.notes and \
            note_id in self.notes[contact_id]

    def add_note(self, contact_id, note):
        if contact_id not in self.notes:
            self.notes[contact_id] = {}
        self.notes[contact_id][note.note_id] = note

    def get_note(self, contact_id, note_id):
        if not self.has_note(contact_id, note_id):
            return None
        else:
            return self.notes[contact_id][note_id]

    def delete_note(self, contact_id, note_id):
        if self.has_note(contact_id, note_id):
            del self.notes[contact_id][note_id]

    def delete_all_notes(self, contact_id):
        if self.has_notes(contact_id):
            del self.notes[contact_id]
