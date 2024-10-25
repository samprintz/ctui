from datetime import datetime


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

    def has_note(self, contact, date):
        date_str = datetime.strftime(date, "%Y%m%d")
        return contact.name in self.notes and \
            date_str in self.notes[contact.name]

    def add_note(self, contact, note):
        if contact.name not in self.notes:
            self.notes[contact.name] = {}
        date_str = datetime.strftime(note.date, "%Y%m%d")
        self.notes[contact.name][date_str] = note
        return True

    def get_note(self, contact, date):
        if not self.has_note(contact, date):
            return None
        else:
            date_str = datetime.strftime(date, "%Y%m%d")
            return self.notes[contact.name][date_str]

    def delete_note(self, contact, date):
        if self.has_note(contact, date):
            date_str = datetime.strftime(date, "%Y%m%d")
            del self.notes[contact.name][date_str]

    def delete_all_notes(self, contact):
        if self.has_notes(contact):
            del self.notes[contact.name]
