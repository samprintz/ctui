from datetime import date,datetime
import os
import shutil
from subprocess import call
import pudb #TODO


"""
Store for interaction with the directory with notes about the contacts.
"""
class NotesStore:

    def __init__(self, path, editor_name):
        self.path = path
        self.editor = os.environ.get('EDITOR', editor_name)


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


    def contains_note(self, contact, date):
        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename
        return os.path.isfile(path)


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


    def add_note(self, contact, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if self.contains_note(contact, date):
            #return "Note for {} already exists."
            return self.edit_note(contact, date_str)

        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            call([self.editor, path])
            return "Note added."
        except OSError:
            return "Error: Note not created."


    def edit_note(self, contact, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.contains_note(contact, date):
            #return "Note for doesn't exist."
            return self.add_note(contact, date_str)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            call([self.editor, path])
            return "Note edited."
        except OSError:
            return "Error: Note not edited."


    def delete_note(self, contact, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.contains_note(contact, date):
            return "Error: No note for \"{}\".".format(date_str)

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

