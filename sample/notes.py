import os
import shutil
import pudb #TODO


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

    def contains_contact(self, contact):
        return self.contains_contact_name(contact.name)

    def contains_contact_name(self, name):
        dirname = self.path + name.replace(' ', '_')
        return os.path.isdir(dirname)

    def add_contact(self, contact):
        pass

    def rename_contact(self, contact, new_name):
        assert self.contains_contact(contact)
        assert contact.name != new_name
        assert not self.contains_contact_name(new_name)
        try:
            dirname = self.path + contact.name.replace(' ', '_')
            new_dirname = self.path + new_name.replace(' ', '_')
            os.rename(dirname, new_dirname)
        except Exception:
            raise Exception #TODO

    def delete_contact(self, contact):
        assert self.contains_contact(contact)
        try:
            dirname = self.path + contact.name.replace(' ', '_')
            shutil.rmtree(dirname, ignore_errors=False)
            return True
        except Exception:
            return Exception #TODO

    def add_note(self, contact, note):
        pass

    def delete_note(self, contact, note):
        pass

    def edit_note(self, contact, note):
        pass

