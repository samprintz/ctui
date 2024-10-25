from datetime import datetime
import os
import re

import yaml


class Contact:

    def __init__(self, name, core, attributes=None, gifts=None, notes=None):
        self.name = name

        # TODO Contact shouldn't have core
        self.core = core

        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_id(self):
        return self.name.replace(' ', '_')

    def has_details(self):
        return self.core.rdfstore.has_attributes(self) or \
            self.core.textfilestore.has_gifts(self) or \
            self.core.textfilestore.has_notes(self)

    def load_details(self):
        self.attributes = self.get_attributes()
        self.gifts = self.get_gifts()
        self.notes = self.get_notes()

    # attributes

    def has_attributes(self):
        return self.core.rdfstore.has_attributes(self)

    def get_attributes(self):
        return self.core.rdfstore.get_attributes(self)

    def has_attribute(self, attribute):
        return self.core.rdfstore.has_attribute(self, attribute)

    def add_attribute(self, attribute):
        return self.core.rdfstore.add_attribute(self, attribute)

    def edit_attribute(self, old_attr, new_attr):
        if old_attr.key == "givenName":  # special case: rename
            return self.core.rename_contact(self, new_attr.value)

        if not self.has_attribute(old_attr):
            return "Error: {} doesn't own attribute {}={}.".format(
                self.name, old_attr.key, old_attr.value)

        if old_attr.key == new_attr.key and old_attr.value == new_attr.value:
            return "Warning: Attribute unchanged."

        return self.core.rdfstore.edit_attribute(self, old_attr, new_attr)

    def delete_attribute(self, attribute):
        if not self.has_attribute(attribute):
            return "Error: {} doesn't own attribute {}={}.".format(
                self.name, attribute.key, attribute.value)

        return self.core.rdfstore.delete_attribute(self, attribute)

    # gifts

    def has_gifts(self):
        return self.core.textfilestore.has_gifts(self)

    def get_gifts(self):
        return self.core.textfilestore.get_gifts(self)

    def get_gifts_path(self):
        return self.core.textfilestore.get_textfile_path_by_type(self.get_id(),
                                                                 self.core.textfilestore.GIFTS_DIR)

    def has_gift(self, gift_id):
        return self.core.textfilestore.has_gift(self.get_id(), gift_id)

    def get_gift(self, gift_id):
        if not self.has_gift(gift_id):
            return "Error: Gift doesn't exist."

        return self.core.textfilestore.get_gift(self, gift_id)

    def add_gift(self, gift):
        return self.core.textfilestore.add_gift(self, gift)

    def edit_gift(self, old_gift, new_gift):
        if not self.has_gift(old_gift.get_id()):
            return "Error: {} doesn't own gift {}.".format(
                self.name, old_gift.name)

        if old_gift == new_gift:
            return "Warning: Gift unchanged."

        # TODO adapt and align the behavior for notes:

        # edit vs. update?

        # how would an interface for notes and gifts look like?
        # how would an interface for note store and gift *store* look like?

        # do in need to add the contact id as attribute to notes and gifts
        #   to remove some of these methods here from Contact?

        filepath = os.path.join(self.get_gifts_path(), date_str)

        try:
            new_content = self.core.editor.edit(filepath)
        except OSError:
            return "Error: Gift couldn't be edited."

        return self.core.textfilestore.edit_gift(self, date, new_content)

        # TODO end

        return self.core.textfilestore.edit_gift(self, old_gift, new_gift)

    def delete_gift(self, gift):
        if not self.has_gift(gift.get_id()):
            return "Error: {} doesn't own gift {}.".format(
                self.name, gift.name)

        return self.core.textfilestore.delete_gift(self, gift)

    def mark_gifted(self, gift):
        return self.core.textfilestore.mark_gifted(self, gift)

    def unmark_gifted(self, gift):
        return self.core.textfilestore.unmark_gifted(self, gift)

    def mark_permanent(self, gift):
        return self.core.textfilestore.mark_permanent(self, gift)

    def unmark_permanent(self, gift):
        return self.core.textfilestore.unmark_permanent(self, gift)

    # notes

    def has_notes(self):
        return self.core.textfilestore.has_notes(self)

    def has_encrypted_notes(self):
        return self.core.textfilestore.has_encrypted_notes(self)

    def get_notes(self):
        return self.core.textfilestore.get_notes(self)

    def get_notes_path(self):
        return self.core.textfilestore.get_textfile_path_by_type(self.get_id(),
                                                                 self.core.textfilestore.NOTES_DIR)

    def has_note(self, date):
        return self.core.textfilestore.has_note(self, date)

    def get_note(self, date):
        if not self.has_note(date):
            return "Error: Note doesn't exist."
        return self.core.textfilestore.get_note(self, date)

    def add_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.core.textfilestore.contains_contact(self):
            self.core.textfilestore.add_contact(self)

        if self.has_note(date):
            return self.edit_note(date_str)

        try:
            content = self.core.editor.add(self.get_notes_path(), date_str)
            note = Note(date, content)
        except OSError:
            return "Error: Note couldn't be added."

        return self.core.textfilestore.add_note(self, note)

    def add_encrypted_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.core.textfilestore.contains_contact(self):
            self.core.textfilestore.add_contact(self)

        if self.has_note(date):
            return self.edit_note(date_str)

        try:
            content = self.core.editor.add(self.get_notes_path(), date_str)
            note = EncryptedNote(date, content)
        except OSError:
            return "Error: Note couldn't be added."

        return self.core.textfilestore.add_encrypted_note(self, note)

    def rename_note(self, note, date_str):
        try:
            new_date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "Error: \"{}\" not in format YYYYMMDD.".format(date_str)

        if note.date == new_date:
            return "Warning: Name unchanged."

        if self.has_note(new_date):
            return "Error: Note {} already exists.".format(date_str)

        return self.core.textfilestore.rename_note(self, note, new_date)

    def delete_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.has_note(date):
            return "Error: No note for \"{}\".".format(date_str)

        return self.core.textfilestore.delete_note(self, date)

    def edit_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.has_note(date):
            return self.add_note(self, date_str)

        filename = f'{date_str}.txt'
        path = os.path.join(self.get_notes_path(), filename)

        try:
            new_content = self.core.editor.edit(path)
        except OSError:
            return "Error: Note couldn't be edited."

        return self.core.textfilestore.edit_note(self, date, new_content)

    def encrypt_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(date):
            return "Note \"{}\" not found.".format(date_str)

        return self.core.textfilestore.encrypt_note(self, date)

    def decrypt_note(self, date_str, passphrase=None):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(date):
            return "Note \"{}\" not found.".format(date_str)

        return self.core.textfilestore.decrypt_note(self, date, passphrase)

    def toggle_note_encryption(self, date_str, passphrase=None):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(date):
            return "Note \"{}\" not found.".format(date_str)

        if self.core.memorystore.has_note(self, date):  # hide
            content = self.core.memorystore.delete_note(self, date)
            return "Hide encrypted note content."
        else:  # show
            content = self.core.textfilestore.get_encrypted_note_text(self,
                                                                      date,
                                                                      passphrase)
            note = EncryptedNote(date, content)
            if self.core.memorystore.add_note(self, note):
                return "Show encrypted note content."
            else:
                return "Failed to show encrypted note content."

    def show_all_encrypted_notes(self, passphrase=None):
        if not self.has_encrypted_notes():
            return "No encrypted notes found."

        result = True
        for note in self.core.textfilestore.get_encrypted_notes(self):
            content = self.core.textfilestore.get_encrypted_note_text(self,
                                                                      note.date,
                                                                      passphrase)
            note = EncryptedNote(note.date, content)
            if not self.core.memorystore.add_note(self, note):
                result = False

        if result:
            return "Show content of all encrypted notes."
        else:
            return "Failed to show content of all encrypted notes."

    def hide_all_encrypted_notes(self, passphrase=None):
        if not self.core.memorystore.has_notes(self):
            return "All encrypted notes are hidden."

        if self.core.memorystore.delete_all_notes(self):
            return "Hide content of all encrypted notes."
        else:
            return "Failed to hide content of all encrypted notes."

    # memory

    def has_visible_note(self, note):
        return self.core.memorystore.has_note(self, note.date)

    def get_visible_note(self, note):
        return self.core.memorystore.get_note(self, note.date)


class Name:

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


class Attribute:

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value


class Gift:

    def __init__(self, name, desc='', permanent=False, gifted=False,
                 occasions=None):
        if re.search(r'[^a-zA-Z0-9äöüÄÖÜß -]', name):
            raise ValueError(
                "Failed to create Gift: name contains invalid characters. Only alphanumeric characters spaces and hypens are allowed.")

        self.name = name
        self.desc = desc
        self.permanent = permanent
        self.gifted = gifted
        self.occasions = occasions

    def __eq__(self, other):
        return self.name == other.name \
            and self.desc == other.desc \
            and self.gifted == other.gifted \
            and self.permanent == other.permanent \
            and self.occasions == other.occasions

    def get_id(self):
        return self.name.replace(' ', '_')

    def to_dict(self):
        data = {}

        if self.permanent:
            data['permanent'] = self.permanent

        if self.gifted:
            data['gifted'] = self.gifted

        if self.occasions is not None:
            data['occasions'] = self.occasions

        return data

    def to_dump(self):
        dump = ''

        gift_dict = self.to_dict()
        if gift_dict:
            dump = yaml.dump(gift_dict, default_flow_style=False)

        return dump

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            desc=data.get("desc"),
            permanent=data.get("permanent"),
            gifted=data.get("gifted"),
            occasions=data.get("occasions", [])
        )

    @classmethod
    def from_dump(self, gift_id, dump):
        data = {}

        if dump:
            data = yaml.safe_load(dump)

        data['name'] = gift_id.replace('_', ' ')

        return Gift.from_dict(data)


class Note:

    def __init__(self, date, content):
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y%m%d')
            except ValueError:
                raise ValueError(
                    f'Invalid note name: "{date}". Note names match the pattern YYYYMMMDD')
        self.date = date
        self.content = content

    def __eq__(self, other):
        return self.date == other.date


class EncryptedNote(Note):

    def __init__(self, date, content=None, encrypted=True):
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y%m%d')
            except ValueError:
                raise ValueError(
                    f'Invalid note name: "{date}". Note names match the pattern YYYYMMMDD')
        self.date = date
        self.content = content

    def __eq__(self, other):
        return self.date == other.date


class GoogleContact(Contact):

    def __init__(self, name, core, google_id, google_attributes=None,
                 google_notes=None):
        super(GoogleContact, self).__init__(name, core)
        self.google_id = google_id
        self.google_attributes = google_attributes
        self.google_notes = google_notes

    def merge(self, contact):
        self.attributes = contact.attributes
        self.gifts = contact.gifts
        self.notes = contact.notes
        return self


class GoogleAttribute:

    def __init__(self, key, value, google_key):
        self.key = key
        self.value = value
        self.google_key = google_key

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value


class GoogleNote:

    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        return self.content == other.content
