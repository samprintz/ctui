import copy
import os
import shutil
from datetime import datetime

import gnupg

from ctui.objects import Note, EncryptedNote, Attribute, Gift


class TextFileStore:
    """
    Store for interaction with the directory with text files about the contacts.
    """

    NOTES_DIR = 'notes'
    GIFTS_DIR = 'gifts'

    def __init__(self, path, gpg_keyid):
        self.path = path
        self.gpg = gnupg.GPG()
        self.gpg_keyid = gpg_keyid

    def get_textfile_path(self, contact_id):
        return os.path.join(self.path, contact_id)

    def get_textfile_path_by_type(self, contact_id, type):
        return os.path.join(self.get_textfile_path(contact_id), type)

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
        dirname = self.get_textfile_path(contact.get_id())
        try:
            os.makedirs(dirname)
        except OSError:
            return "Couldn't create directory \"{}\".".format(dirname)

    def rename_contact(self, contact, new_name):
        assert self.contains_contact(contact)
        assert contact.name != new_name
        assert not self.contains_contact_name(new_name)

        try:
            dirname = self.get_textfile_path(contact.get_id())
            new_dirname = self.path + new_name.replace(' ', '_')
            os.rename(dirname, new_dirname)
        except OSError:
            return "Couldn't rename directory \"{}\" to \"{}\"." \
                .format(dirname, new_dirname)

    def delete_contact(self, contact):
        assert self.contains_contact(contact)

        try:
            dirname = self.get_textfile_path(contact.get_id())
            shutil.rmtree(dirname, ignore_errors=False)
            return True
        except Exception:
            return "Couldn't delete directory \"{}\".".format(dirname)

    def has_entries(self, contact, type):
        dir_path = self.get_textfile_path_by_type(contact.get_id(), type)
        return os.path.isdir(dir_path) and len(os.listdir(dir_path)) > 0

    def has_notes(self, contact):
        return self.has_entries(contact, self.NOTES_DIR)

    def has_encrypted_notes(self, contact):
        dirname = self.get_textfile_path(contact.get_id())
        if not self.has_notes(contact):
            return False
        for file in os.listdir(dirname):
            if file.endswith(".gpg"):
                return True

    def get_notes(self, contact):
        """
        Read plain text and encrypted notes of a given contact and return a
        list of both of them.
        """
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        notes = []
        try:
            for filename in sorted(os.listdir(dirname)):

                # plain notes
                if not filename.endswith(".gpg"):
                    date = filename.replace('.txt', '')
                    file_path = os.path.join(dirname, filename)

                    with open(file_path, "r") as f:
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

    def get_encrypted_notes(self, contact):
        """
        Read encrypted notes of a given contact and return a list of them.
        """
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        notes = []
        try:
            for filename in sorted(os.listdir(dirname)):
                if filename.endswith(".gpg"):
                    date = filename.replace('.txt', '').replace('.gpg', '')
                    note = EncryptedNote(date)
                    notes.append(note)
            return notes
        except FileNotFoundError:
            return None

    def has_note(self, contact, date):
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename
        return os.path.isfile(path) or os.path.isfile(
            path + ".gpg")  # plain or encrypted notes

    def note_is_encrypted(self, contact, date):
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt.gpg"
        path = dirname + '/' + filename
        return os.path.isfile(path)

    def get_note(self, contact, date):
        assert self.has_note(contact, date)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            with open(path, "r") as f:
                content = f.read()
                return content.strip()
        except OSError:
            return "Couldn't read note"

    def add_note(self, contact, note):
        assert not self.has_note(contact, note.date)

        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            with open(path, 'w') as f:
                f.write(note.content)
            return "Note added."
        except OSError:
            return "Error: Note not created."

    def add_encrypted_note(self, contact, note):
        assert not self.has_note(contact, note.date)

        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
        path = dirname + '/' + filename

        try:
            # write to (normal) file
            with open(path, 'w') as f:
                f.write(note.content)
            # encrypt that file
            with open(path, 'rb') as f:
                status = self.gpg.encrypt_file(
                    f, recipients=[self.gpg_keyid], output=f'{path}.gpg')
            # delete plain text file
            os.remove(path)
            return f"Note added (ok: {status.ok})."
        except OSError:
            return "Error: Note not created."

    def rename_note(self, contact, note, new_date):
        assert note.date != new_date
        assert self.has_note(contact, note.date)
        assert not self.has_note(contact, new_date)

        if self.note_is_encrypted(contact, note.date):
            old_filename = datetime.strftime(note.date, "%Y%m%d") + ".txt.gpg"
            new_filename = datetime.strftime(new_date, "%Y%m%d") + ".txt.gpg"
        else:
            old_filename = datetime.strftime(note.date, "%Y%m%d") + ".txt"
            new_filename = datetime.strftime(new_date, "%Y%m%d") + ".txt"

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        old_path = dirname + '/' + old_filename
        new_path = dirname + '/' + new_filename

        try:
            os.rename(old_path, new_path)
            return "Note renamed."
        except OSError:
            return "Error: Note not renamed."

    def delete_note(self, contact, date):
        assert self.has_note(contact, date)

        if self.note_is_encrypted(contact, date):
            filename = datetime.strftime(date, "%Y%m%d") + ".txt.gpg"
        else:
            filename = datetime.strftime(date, "%Y%m%d") + ".txt"

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
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
        assert self.has_note(contact, date)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)

        filename = f'{datetime.strftime(date, "%Y%m%d")}.txt'
        path = os.path.join(dirname, filename)

        try:
            with open(path, 'w') as f:
                f.write(new_content)
            return "Note edited."
        except OSError:
            return "Error: Note not edited."

    def encrypt_note(self, contact, date):
        assert self.has_note(contact, date)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path_plain = dirname + '/' + filename
        path_encrypt = dirname + '/' + filename + ".gpg"

        # check if key available
        if not self.is_key_in_keyring():
            return "GPG key not found in keyring"

        try:
            # encrypt file
            with open(path_plain,
                      'rb') as f:  # "rb" is important, "r" doesn't work
                status = self.gpg.encrypt_file(
                    f, recipients=[self.gpg_keyid], output=path_encrypt)
            # delete plain file
            if status.ok:
                os.remove(path_plain)
            return f"Note encrypted (ok: {status.ok})."
        except OSError:
            return "Error: Note not encrypted."

    def decrypt_note(self, contact, date, passphrase=None):
        assert self.has_note(contact, date)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path_plain = dirname + '/' + filename
        path_encrypt = dirname + '/' + filename + ".gpg"

        # check if key available
        if not self.is_key_in_keyring():
            return "GPG key not found in keyring"

        try:
            # decrypt file
            with open(path_encrypt, 'rb') as f:
                # passphrase is always None, the gpg-agent is taking care of it
                status = self.gpg.decrypt_file(
                    f, passphrase=passphrase, output=path_plain)
            if status.ok:
                # delete encrypted file
                os.remove(path_encrypt)
                return "Note decrypted"
            else:
                return "Wrong passphrase"
        except OSError:
            return "Error: Note not decrypted."

    def get_encrypted_note_text(self, contact, date, passphrase=None):
        assert self.has_note(contact, date)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.NOTES_DIR)
        filename = datetime.strftime(date, "%Y%m%d") + ".txt"
        path_plain = dirname + '/' + filename
        path_encrypt = dirname + '/' + filename + ".gpg"

        try:
            # decrypt file
            with open(path_encrypt, 'rb') as f:
                # passphrase is always None, the gpg-agent is taking care of it
                status = self.gpg.decrypt_file(
                    f, passphrase=passphrase, output=path_plain)
            if status.ok:
                # read decrypted file
                with open(path_plain) as f:
                    content = f.read()
                # delete decrypted file again
                # TODO Is there a way to not even create the decrypted file?
                os.remove(path_plain)
                return content.strip()
            else:
                return "Wrong passphrase"
        except OSError:
            return "Error: Note not decrypted."

    def is_key_in_keyring(self):
        found_public_key = False
        found_private_key = False

        public_keys = self.gpg.list_keys()
        for public_key in public_keys:
            if public_key['keyid'] == self.gpg_keyid:
                found_public_key = True

        private_keys = self.gpg.list_keys(True)
        for private_key in private_keys:
            if private_key['keyid'] == self.gpg_keyid:
                found_private_key = True

        return found_public_key and found_private_key
        # TODO Log whether both or only one of them is missing

    def has_gifts(self, contact):
        return self.has_entries(contact, self.GIFTS_DIR)

    def get_gifts(self, contact):
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.GIFTS_DIR)
        gifts = []
        try:
            for filename in sorted(os.listdir(dirname)):
                gift_id = filename.replace('.yaml', '')
                file_path = os.path.join(dirname, filename)

                with open(file_path, "r") as f:
                    lines = f.read()
                    gift = Gift.from_dump(gift_id, lines)
                    gifts.append(gift)

            return gifts
        except FileNotFoundError:
            return None

    def has_gift(self, contact_id, gift_id):
        dirname = self.get_textfile_path_by_type(contact_id, self.GIFTS_DIR)
        filename = f"{gift_id}.yaml"
        path = os.path.join(dirname, filename)
        return os.path.isfile(path)

    def get_gift(self, contact, gift_id):
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.GIFTS_DIR)
        filename = f"{gift_id}.yaml"
        path = os.path.join(dirname, filename)

        try:
            with open(path, "r") as f:
                lines = f.read()
                return Gift.from_dump(gift_id, lines)
        except OSError:
            return "Couldn't read gift"

    def add_gift(self, contact, gift):
        if not self.contains_contact(contact):
            self.add_contact(contact)

        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.GIFTS_DIR)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        filename = f'{gift.get_id()}.yaml'
        path = os.path.join(dirname, filename)

        textfile_content = gift.to_dump()

        try:
            with open(path, 'w') as f:
                f.write(textfile_content)
            return "Gift added."
        except OSError:
            return "Error: Gift not created."

    def edit_gift(self, contact, old_gift, new_gift):
        self.delete_gift(contact, old_gift)

        try:
            # TODO this never throws, but should throw OSError
            self.add_gift(contact, new_gift)

            return "Gift edited."
        except OSError:
            return "Error: Gift not edited."

    def delete_gift(self, contact, gift):
        filename = f'{gift.get_id()}.yaml'
        dirname = self.get_textfile_path_by_type(contact.get_id(),
                                                 self.GIFTS_DIR)
        path = os.path.join(dirname, filename)

        try:
            os.remove(path)
            # if this was the last gift, delete the directory
            if len(os.listdir(dirname)) == 0:
                os.rmdir(dirname)
            return "Gift deleted."
        except OSError:
            return "Error: Gift not deleted."

    def mark_gifted(self, contact, gift):
        new_gift = copy.deepcopy(gift)
        new_gift.gifted = True
        return self.edit_gift(contact, gift, new_gift)

    def unmark_gifted(self, contact, gift):
        new_gift = copy.deepcopy(gift)
        new_gift.gifted = False
        return self.edit_gift(contact, gift, new_gift)

    def mark_permanent(self, contact, gift):
        new_gift = copy.deepcopy(gift)
        new_gift.permanent = True
        return self.edit_gift(contact, gift, new_gift)

    def unmark_permanent(self, contact, gift):
        new_gift = copy.deepcopy(gift)
        new_gift.permanent = False
        return self.edit_gift(contact, gift, new_gift)

    # TODO move to new gifts module, filesystem-based analog to notes module

    # TODO add add_occasion(occasion), remove_occasion
