import os
import shutil

import gnupg

from ctui.model.contact import Contact
from ctui.model.detail import Detail
from ctui.model.encrypted_note import EncryptedNote
from ctui.model.gift import Gift
from ctui.model.note import Note


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

    def get_note_filepath(self, contact_id, note_id):
        filename = f'{note_id}.txt'
        return os.path.join(
            self.get_textfile_path_by_type(contact_id, self.NOTES_DIR),
            filename)

    def get_gift_filepath(self, contact_id, gift_id):
        dirname = self.get_textfile_path_by_type(contact_id, self.GIFTS_DIR)
        filename = Gift.id_to_filename(gift_id)
        return os.path.join(dirname, filename)

    def create_contact_dir(self, contact_id):
        dirname = self.get_textfile_path(contact_id)
        try:
            os.makedirs(dirname)
        except OSError:
            return "Couldn't create directory \"{}\".".format(dirname)

    def create_note_dir(self, contact_id):
        return self.create_textfile_dir(contact_id, self.NOTES_DIR)

    def create_gift_dir(self, contact_id):
        return self.create_textfile_dir(contact_id, self.GIFTS_DIR)

    def create_textfile_dir(self, contact_id, textfile_type):
        if not self.contains_contact(contact_id):
            self.create_contact_dir(contact_id)

        path = self.get_textfile_path_by_type(contact_id, textfile_type)

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_contact_names(self):
        contact_names = []
        for dirname in os.listdir(self.path):
            if dirname.endswith('.txt'): continue
            contact_names.append(dirname.replace('_', ' '))
        return sorted(contact_names)

    def contains_contact(self, contact_id):
        dirname = self.path + contact_id
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
        assert not self.contains_contact(Contact.name_to_id(new_name))

        try:
            dirname = self.get_textfile_path(contact.get_id())
            new_dirname = self.path + new_name.replace(' ', '_')
            os.rename(dirname, new_dirname)
        except OSError:
            return "Couldn't rename directory \"{}\" to \"{}\"." \
                .format(dirname, new_dirname)

    def delete_contact(self, contact_id):
        assert self.contains_contact(contact_id)

        try:
            dirname = self.get_textfile_path(contact_id)
            shutil.rmtree(dirname, ignore_errors=False)
            return True
        except Exception:
            return "Couldn't delete directory \"{}\".".format(dirname)

    def has_entries(self, contact_id, detail_type):
        has_entries = False

        if contact_id:
            dir_path = self.get_textfile_path_by_type(contact_id, detail_type)
            has_entries = os.path.isdir(dir_path) \
                          and len(os.listdir(dir_path)) > 0

        return has_entries

    def has_notes(self, contact_id):
        return self.has_entries(contact_id, self.NOTES_DIR)

    def has_encrypted_notes(self, contact_id):
        dirname = self.get_textfile_path_by_type(contact_id, self.NOTES_DIR)
        if not self.has_notes(contact_id):
            return False
        for file in os.listdir(dirname):
            if file.endswith(".gpg"):
                return True

    def get_notes(self, contact_id):
        """
        Read plain text and encrypted notes of a given contact and return a
        list of both of them.
        """
        notes = []

        if self.has_notes(contact_id):
            dirname = self.get_textfile_path_by_type(contact_id, self.NOTES_DIR)

            for filename in sorted(os.listdir(dirname)):

                # plain notes
                if not filename.endswith(".gpg"):
                    file_path = os.path.join(dirname, filename)

                    with open(file_path, "r") as f:
                        content = f.read().strip()
                        note_id = filename.replace('.txt', '')
                        note = Note(note_id, content)
                        notes.append(note)

                # encrypted notes
                else:
                    note_id = filename.replace('.txt', '').replace('.gpg', '')
                    note = EncryptedNote(note_id)
                    notes.append(note)

        return notes

    def get_encrypted_notes(self, contact_id):
        """
        Read encrypted notes of a given contact and return a list of them.
        """
        dirname = self.get_textfile_path_by_type(contact_id, self.NOTES_DIR)
        notes = []

        for filename in sorted(os.listdir(dirname)):
            if filename.endswith(".gpg"):
                note_id = filename.replace('.txt', '').replace('.gpg', '')
                note = EncryptedNote(note_id)
                notes.append(note)
        return notes

    def has_note(self, contact_id, note_id):
        filepath = self.get_note_filepath(contact_id, note_id)
        # plain or encrypted notes
        return os.path.isfile(filepath) or os.path.isfile(filepath + ".gpg")

    def note_is_encrypted(self, contact_id, note_id):
        filepath = self.get_note_filepath(contact_id, note_id) + ".gpg"
        return os.path.isfile(filepath)

    def get_note(self, contact_id, note_id):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note {note_id} doesn\'t exist')

        filepath = self.get_note_filepath(contact_id, note_id)

        with open(filepath, "r") as f:
            content = f.read()
            return Note.from_dump(note_id, content)

    def add_note(self, contact_id, note):
        if self.has_note(contact_id, note.note_id):
            raise ValueError(f'Note "{note.note_id}" already exists')

        self.create_note_dir(contact_id)

        filepath = self.get_note_filepath(contact_id, note.note_id)
        content = note.to_dump()

        with open(filepath, 'w') as f:
            f.write(content)

        return "Note added"

    def add_encrypted_note(self, contact_id, note):
        if self.has_note(contact_id, note.note_id):
            raise ValueError(f'Note "{note.note_id}" already exists')

        self.create_note_dir(contact_id)

        filepath = self.get_note_filepath(contact_id, note.note_id)

        # write to (normal) file
        with open(filepath, 'w') as f:
            f.write(note.content)

        # encrypt that file
        with open(filepath, 'rb') as f:
            status = self.gpg.encrypt_file(
                f, recipients=[self.gpg_keyid], output=f'{filepath}.gpg')

        # delete plain text file
        os.remove(filepath)
        return f'Note added (ok: {status.ok}).'

    def rename_note(self, contact_id, note_id, new_name):
        new_note_id = Note.name_to_id(new_name)

        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        if self.has_note(contact_id, new_note_id):
            raise ValueError(
                f'Can\'t rename note as "{new_note_id}" already exists')

        old_filepath = self.get_note_filepath(contact_id, note_id)
        new_filepath = self.get_note_filepath(contact_id, new_note_id)

        if self.note_is_encrypted(contact_id, note_id):
            old_filepath = f'{old_filepath}.gpg'
            new_filepath = f'{new_filepath}.gpg'

        os.rename(old_filepath, new_filepath)
        return "Note renamed"

    def edit_note(self, contact_id, note_id, note):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        filepath = self.get_note_filepath(contact_id, note_id)

        dump = note.to_dump()

        with open(filepath, 'w') as f:
            f.write(dump)

        return "Note edited"

    def delete_note(self, contact_id, note_id):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note {note_id} doesn\'t exist')

        filepath = self.get_note_filepath(contact_id, note_id)

        if self.note_is_encrypted(contact_id, note_id):
            filepath = f'{filepath}.gpg'

        os.remove(filepath)

        # if this was the last note, delete the directory
        dirname = self.get_textfile_path_by_type(contact_id, self.NOTES_DIR)
        if len(os.listdir(dirname)) == 0:
            os.rmdir(dirname)

        return "Note deleted"

    def encrypt_note(self, contact_id, note_id):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        filepath_plain = self.get_note_filepath(contact_id, note_id)
        filepath_encrypt = f'{filepath_plain}.gpg'

        if not self.is_key_in_keyring():
            raise ValueError('GPG key not found in keyring')

        # "rb" is important, "r" doesn't work
        with open(filepath_plain, 'rb') as f:
            status = self.gpg.encrypt_file(f, recipients=[self.gpg_keyid],
                                           output=filepath_encrypt)

        # delete plain file
        if status.ok:
            os.remove(filepath_plain)

        return f'Note encrypted (ok: {status.ok})'

    def decrypt_note(self, contact_id, note_id, passphrase=None):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        filepath_plain = self.get_note_filepath(contact_id, note_id)
        filepath_encrypt = f'{filepath_plain}.gpg'

        if not self.is_key_in_keyring():
            raise ValueError('GPG key not found in keyring')

        with open(filepath_encrypt, 'rb') as f:
            # passphrase is always None, the gpg-agent is taking care of it
            status = self.gpg.decrypt_file(f, passphrase=passphrase,
                                           output=filepath_plain)
        if status.ok:
            # delete encrypted file
            os.remove(filepath_encrypt)
            return "Note decrypted"
        else:
            return "Wrong passphrase"

    def get_encrypted_note_text(self, contact_id, note_id, passphrase=None):
        if not self.has_note(contact_id, note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        filepath_plain = self.get_note_filepath(contact_id, note_id)
        filepath_encrypt = f'{filepath_plain}.gpg'

        with open(filepath_encrypt, 'rb') as f:
            # passphrase is always None, the gpg-agent is taking care of it
            status = self.gpg.decrypt_file(f, passphrase=passphrase,
                                           output=filepath_plain)
        if status.ok:
            # read decrypted file
            with open(filepath_plain) as f:
                content = f.read()
            # delete decrypted file again
            # TODO Is there a way to not even create the decrypted file?
            os.remove(filepath_plain)
            return content.strip()
        else:
            return "Wrong passphrase"

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

    def has_gifts(self, contact_id):
        return self.has_entries(contact_id, self.GIFTS_DIR)

    def get_gifts(self, contact_id):
        gifts = []

        if self.has_gifts(contact_id):
            dirname = self.get_textfile_path_by_type(contact_id, self.GIFTS_DIR)

            for filename in sorted(os.listdir(dirname)):
                gift_id = filename.replace('.yaml', '')
                file_path = os.path.join(dirname, filename)

                with open(file_path, "r") as f:
                    lines = f.read()

                    try:
                        gift = Gift.from_dump(gift_id, lines)
                    except ValueError as error:
                        gift = Detail(f'⚠️ {error}')

                    gifts.append(gift)

        return gifts

    def has_gift(self, contact_id, gift_id):
        filepath = self.get_gift_filepath(contact_id, gift_id)
        return os.path.isfile(filepath)

    def get_gift(self, contact_id, gift_id):
        if not self.has_gift(contact_id, gift_id):
            raise ValueError(f'Gift {gift_id} does not exist')

        filepath = self.get_gift_filepath(contact_id, gift_id)

        with open(filepath, "r") as f:
            content = f.read()
            return Gift.from_dump(gift_id, content)

    def add_gift(self, contact_id, gift):
        if self.has_gift(contact_id, gift.get_id()):
            raise ValueError(f'Gift "{gift.get_id()}" already exists')

        self.create_gift_dir(contact_id)

        filepath = self.get_gift_filepath(contact_id, gift.get_id())
        content = gift.to_dump()

        with open(filepath, 'w') as f:
            f.write(content)

        return "Gift added"

    def rename_gift(self, contact_id, gift_id, new_name):
        new_gift_id = Gift.name_to_id(new_name)

        if not self.has_gift(contact_id, gift_id):
            ValueError(f'Gift "{gift_id}" doesn\'t exist')

        if self.has_gift(contact_id, new_gift_id):
            ValueError(f'Can\'t rename note as "{new_gift_id}" already exist')

        old_filepath = self.get_gift_filepath(contact_id, gift_id)
        new_filepath = self.get_gift_filepath(contact_id, new_gift_id)

        os.rename(old_filepath, new_filepath)
        return "Gift renamed"

    def edit_gift(self, contact_id, gift_id, gift):
        if not self.has_gift(contact_id, gift_id):
            raise ValueError(f'Gift {gift_id} doesn\'t exist')

        filepath = self.get_gift_filepath(contact_id, gift_id)

        dump = gift.to_dump()

        with open(filepath, 'w') as f:
            f.write(dump)

        return "Gift edited"

    def delete_gift(self, contact_id, gift_id):
        if not self.has_gift(contact_id, gift_id):
            raise ValueError(f'Gift "{gift_id}" doesn\'t exist')

        filepath = self.get_gift_filepath(contact_id, gift_id)

        os.remove(filepath)

        # if this was the last gift, delete the directory
        dirname = self.get_textfile_path_by_type(contact_id, self.GIFTS_DIR)
        if len(os.listdir(dirname)) == 0:
            os.rmdir(dirname)

        return "Gift deleted"

    def mark_gifted(self, contact_id, gift_id):
        gift = self.get_gift(contact_id, gift_id)
        gift.gifted = True
        return self.edit_gift(contact_id, gift_id, gift)

    def unmark_gifted(self, contact_id, gift_id):
        gift = self.get_gift(contact_id, gift_id)
        gift.gifted = False
        return self.edit_gift(contact_id, gift_id, gift)

    def mark_permanent(self, contact_id, gift_id):
        gift = self.get_gift(contact_id, gift_id)
        gift.permanent = True
        return self.edit_gift(contact_id, gift_id, gift)

    def unmark_permanent(self, contact_id, gift_id):
        gift = self.get_gift(contact_id, gift_id)
        gift.permanent = False
        return self.edit_gift(contact_id, gift_id, gift)

    # TODO move to new gifts module, filesystem-based analog to notes module

    # TODO add add_occasion(occasion), remove_occasion
