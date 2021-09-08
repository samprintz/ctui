from datetime import date,datetime
import gnupg
import os
import shutil
from subprocess import call

from objects import Note, EncryptedNote


"""
Store for interaction with the directory with notes about the contacts.
"""
class NotesStore:

    def __init__(self, path):
        self.path = path
        self.gpg = gnupg.GPG()


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
        """
        Read plain text and encrypted notes of a given contact and return a
        list of both of them.
        """
        dirname = self.path + contact.name.replace(' ', '_')
        notes = []
        try:
            for filename in sorted(os.listdir(dirname)):

                # plain notes
                if 'gpg' not in filename:
                    date = filename.replace('.txt', '')
                    with open(dirname + '/' + filename, "r") as f:
                        content = f.read().strip()
                        note = Note(date, content)
                        notes.append(note)

                # encrypted notes
                else:
                    date = filename.replace('.txt', '').replace('.gpg', '')
                    note = EncryptedNote(date)
                    notes.append(note)

            return notes
        except FileNotFoundError:
            return None


    def contains_note(self, contact, date):
        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename
        return os.path.isfile(path) or os.path.isfile(path + ".gpg") # plain or encrypted notes


    def note_is_encrypted(self, contact, date):
        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt.gpg"
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


    def add_encrypted_note(self, contact, note):
        assert not self.contains_note(contact, note.date)

        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            # write to (normal) file
            with open(path, 'w') as f:
                f.write(note.content)
            # encrypt that file
            with open(path, 'rb') as f:
                status = self.gpg.encrypt_file(
                    f, recipients=['343EFE5987C5F0B9'], output=f'{path}.gpg')
            # delete plain text file
            os.remove(path)
            return f"Note added (ok: {status.ok})."
        except OSError:
            return "Error: Note not created."


    def rename_note(self, contact, note, new_date):
        assert note.date != new_date
        assert self.contains_note(contact, note.date)
        assert not self.contains_note(contact, new_date)

        if self.note_is_encrypted(contact, note.date):
            old_filename = datetime.strftime(note.date, "%Y%m%d") + ".txt.gpg"
            new_filename = datetime.strftime(new_date, "%Y%m%d") + ".txt.gpg"
        else:
            old_filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
            new_filename = datetime.strftime(new_date, "%Y%m%d") + ".txt"

        dirname = self.path + contact.name.replace(' ', '_')
        old_path = dirname + '/' + old_filename
        new_path = dirname + '/' + new_filename

        try:
            os.rename(old_path, new_path)
            return "Note renamed."
        except OSError:
            return "Error: Note not renamed."


    def delete_note(self, contact, date):
        assert self.contains_note(contact, date)

        if self.note_is_encrypted(contact, date):
            filename = datetime.strftime(date, "%Y%m%d") + ".txt.gpg"
        else:
            filename = datetime.strftime(date, "%Y%m%d") + ".txt"

        dirname = self.path + contact.name.replace(' ', '_')
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


    def encrypt_note(self, contact, date):
        assert self.contains_note(contact, date)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path_plain = dirname + '/' + filename
        path_encrypt = dirname + '/' + filename + ".gpg"

        try:
            # encrypt file
            with open(path_plain, 'rb') as f: # "rb" is important, "r" doesn't work
                status = self.gpg.encrypt_file(
                    f, recipients=['343EFE5987C5F0B9'], output=path_encrypt)
            # delete plain file
            os.remove(path_plain)
            return f"Note encrypted (ok: {status.ok})."
        except OSError:
            return "Error: Note not encrypted."


    def decrypt_note(self, contact, date, passphrase):
        assert self.contains_note(contact, date)

        dirname = self.path + contact.name.replace(' ', '_')
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path_plain = dirname + '/' + filename
        path_encrypt = dirname + '/' + filename + ".gpg"

        try:
            # decrypt file
            with open(path_encrypt, 'rb') as f:
                status = self.gpg.decrypt_file(
                        f, passphrase=passphrase, output=path_plain)
            if status.ok: # Note for debugging: GPG might remember a correct passphrase for few minutes
                # delete encrypted file
                os.remove(path_encrypt)
                return "Note decrypted"
            else:
                return "Wrong passphrase"
        except OSError:
            return "Error: Note not decrypted."
