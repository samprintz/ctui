import os


"""
Store for interaction with the directory with notes about the contacts.
"""
class NotesStore:
    def __init__(self, path):
        self.path = path

    def get_all_contact_names(self):
        contact_names = []
        for dirname in os.listdir(self.path):
            if dirname.endswith('.txt'): continue
            contact_names.append(dirname.replace('_', ' '))
        return sorted(contact_names)

    def get_notes(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        notes = dict()
        try:
            for filename in os.listdir(dirname):
                date = filename.replace('.txt', '')
                with open(dirname + '/' + filename, "r") as f:
                    content = f.read()
                    notes[date] = content.strip()
            return notes
        except FileNotFoundError:
            return None

    def has_notes(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        return os.path.isdir(dirname) and len(os.listdir(dirname)) > 0

    def has_directory(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        return os.path.isdir(dirname)

    def add_note(self, contact, note):
        pass

    def delete_note(self, contact, note):
        pass

    def edit_note(self, contact, note):
        pass

