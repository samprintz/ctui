from datetime import date,datetime
import os
import shutil
from subprocess import call
import pudb #TODO


"""
Store for interaction with the directory with notes about the contacts.
"""
class NotesStore:

    def __init__(self, path):
        self.path = path


    def get_notes_path(self, contact):
        return self.path + contact.name.replace(' ', '_')


    def get_all_contact_names(self):
        contact_names = []
        for dirname in os.listdir(self.path):
            if dirname.endswith('.txt'): continue
            contact_names.append(dirname.replace('_', ' '))
        return sorted(contact_names)


    def contains_contact(self, contact):
        return self.contains_contact_name(contact.name)


    def contains_contact_name(self, name):
        dirname = self.path + name.replace(' ', '_')
        return os.path.isdir(dirname)


    def add_contact(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        try:
            os.makedirs(dirname)
        except OSError:
            return "Couldn't create directory \"{}\".".format(dirname)


    def rename_contact(self, contact, new_name):
        assert self.contains_contact(contact)
        assert contact.name != new_name
        assert not self.contains_contact_name(new_name)

        try:
            dirname = self.path + contact.name.replace(' ', '_')
            new_dirname = self.path + new_name.replace(' ', '_')
            os.rename(dirname, new_dirname)
        except OSError:
            return "Couldn't rename directory \"{}\" to \"{}\"." \
                    .format(dirname, new_dirname)


    def delete_contact(self, contact):
        assert self.contains_contact(contact)

        try:
            dirname = self.path + contact.name.replace(' ', '_')
            shutil.rmtree(dirname, ignore_errors=False)
            return True
        except Exception:
            return "Couldn't delete directory \"{}\".".format(dirname)


    def has_notes(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        return os.path.isdir(dirname) and len(os.listdir(dirname)) > 0


    def get_notes(self, contact):
        dirname = self.path + contact.name.replace(' ', '_')
        notes = dict()
        try:
            for filename in sorted(os.listdir(dirname)):
                date = filename.replace('.txt', '')
                with open(dirname + '/' + filename, "r") as f:
                    content = f.read()
                    notes[date] = content.strip()
            return notes
        except FileNotFoundError:
            return None


    def contains_note(self, contact, date):
        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename
        return os.path.isfile(path)


    def get_note(self, contact, date):
        assert self.contains_note(contact, date)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            with open(path, "r") as f:
                content = f.read()
                return content.strip()
        except OSError:
            return "Couldn't read note"


    def add_note(self, contact, note):
        assert not self.contains_note(contact, note.date)

        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            with open(path, 'w') as f:
                f.write(note.content)
            return "Note added."
        except OSError:
            return "Error: Note not created."


    def rename_note(self, contact, note, new_date):
        assert note.date != new_date
        assert self.contains_note(contact, note.date)
        assert not self.contains_note(contact, new_date)

        dirname = self.path + contact.name.replace(' ', '_')
        old_filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
        old_path = dirname + '/' + old_filename
        new_filename = datetime.strftime(new_date, "%Y%m%d") + ".txt"
        new_path = dirname + '/' + new_filename

        try:
            os.rename(old_path, new_path)
            return "Note renamed."
        except OSError:
            return "Error: Note not renamed."


    def delete_note(self, contact, date):
        assert self.contains_note(contact, date)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            os.remove(path)
            # if this was the last note, delete the directory
            if len(os.listdir(dirname)) == 0:
                os.rmdir(dirname)
            return "Note deleted."
        except OSError:
            return "Error: Note not deleted."


    def edit_note(self, contact, date, new_content):
        assert self.contains_contact(contact)
        assert self.contains_note(contact, date)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            with open(path, 'w') as f:
                f.write(new_content)
            return "Note edited."
        except OSError:
            return "Error: Note not edited."

