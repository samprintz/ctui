import os

from ctui.model.encrypted_note import EncryptedNote
from ctui.model.gift import Gift
from ctui.model.note import Note


class Contact:

    def __init__(self, name, core, attributes=None, gifts=None, notes=None):
        self.name = name

        # TODO Contact shouldn't have core
        self.core = core

        # TODO interface for notes and gifts
        # TODO interface for note and gift *stores*
        # TODO add contact id as attribute to notes and gifts to remove some of these methods here from Contact?

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

    def has_gift(self, gift_id):
        return self.core.textfilestore.has_gift(self.get_id(), gift_id)

    def get_gift(self, gift_id):
        if not self.has_gift(gift_id):
            return "Error: Gift doesn't exist."

        return self.core.textfilestore.get_gift(self, gift_id)

    def add_gift(self, gift_name):
        Gift.validate_name(gift_name)

        gift_id = gift_name.replace(" ", "_")

        if not self.core.textfilestore.contains_contact(self):
            self.core.textfilestore.add_contact(self)

        if self.has_gift(gift_id):
            return self.edit_gift(gift_id)

        dirname = self.get_gifts_path()

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        try:
            content = self.core.editor.add(dirname, gift_id)
            gift = Gift.from_dump(gift_id, content)
        except OSError:
            return "Error: Gift couldn't be added."

        return self.core.textfilestore.add_gift(self, gift)

    def edit_gift(self, gift_id):
        Gift.validate_name(gift_id)

        if not self.has_gift(gift_id):
            gift_name = gift_id.replace("_", " ")
            return self.add_gift(gift_name)

        filepath = self.core.textfilestore.get_gift_filepath(self.get_id(),
                                                             gift_id)

        try:
            new_content = self.core.editor.edit(filepath)
        except OSError:
            return "Error: Gift couldn't be edited."

        return self.core.textfilestore.edit_gift(self.get_id(), gift_id,
                                                 new_content)

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

    def get_gifts_path(self):
        return self.core.textfilestore.get_textfile_path_by_type(self.get_id(),
                                                                 self.core.textfilestore.GIFTS_DIR)

    def has_note(self, note_id):
        return self.core.textfilestore.has_note(self.get_id(), note_id)

    def get_note(self, note_id):
        if not self.has_note(note_id):
            return "Error: Note doesn't exist."
        return self.core.textfilestore.get_note(self, note_id)

    def add_note(self, note_id):
        Note.validate_name(note_id)

        if not self.core.textfilestore.contains_contact(self):
            self.core.textfilestore.add_contact(self)

        if self.has_note(note_id):
            return self.edit_note(note_id)

        dirname = self.get_notes_path()

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        try:
            content = self.core.editor.add(dirname, note_id)
            note = Note(note_id, content)
        except OSError:
            return "Error: Note couldn't be added."

        return self.core.textfilestore.add_note(self, note)

    def add_encrypted_note(self, note_id):
        Note.validate_name(note_id)

        if not self.core.textfilestore.contains_contact(self):
            self.core.textfilestore.add_contact(self)

        if self.has_note(note_id):
            return self.edit_note(note_id)

        try:
            content = self.core.editor.add(self.get_notes_path(), note_id)
            note = EncryptedNote(note_id, content)
        except OSError:
            return "Error: Note couldn't be added."

        return self.core.textfilestore.add_encrypted_note(self, note)

    def rename_note(self, note, new_name):
        Note.validate_name(new_name)

        if note.note_id == new_name:
            return "Warning: Name unchanged."

        if self.has_note(new_name):
            return "Error: Note {} already exists.".format(new_name)

        return self.core.textfilestore.rename_note(self.get_id(), note,
                                                   new_name)

    def rename_gift(self, gift, new_name):
        Gift.validate_name(new_name)

        if gift.name == new_name:
            return "Warning: Name unchanged."

        if self.has_gift(new_name):
            return "Error: Gift {} already exists.".format(new_name)

        return self.core.textfilestore.rename_gift(self.get_id(), gift,
                                                   new_name)

    def delete_note(self, note_id):
        if not self.has_note(note_id):
            return "Error: No note for \"{}\".".format(note_id)

        return self.core.textfilestore.delete_note(self, note_id)

    def edit_note(self, note_id):
        Note.validate_name(note_id)

        if not self.has_note(note_id):
            return self.add_note(note_id)

        filepath = self.core.textfilestore.get_note_filepath(self.get_id(),
                                                             note_id)

        try:
            new_content = self.core.editor.edit(filepath)
        except OSError:
            return "Error: Note couldn't be edited."

        return self.core.textfilestore.edit_note(self.get_id(), note_id,
                                                 new_content)

    def encrypt_note(self, note_id):
        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(note_id):
            return "Note \"{}\" not found.".format(note_id)

        return self.core.textfilestore.encrypt_note(self, note_id)

    def decrypt_note(self, note_id, passphrase=None):
        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(note_id):
            return "Note \"{}\" not found.".format(note_id)

        return self.core.textfilestore.decrypt_note(self, note_id, passphrase)

    def toggle_note_encryption(self, note_id, passphrase=None):
        if not self.core.textfilestore.contains_contact(self):
            return "Contact \"{}\" not found.".format(self.name)

        if not self.has_note(note_id):
            return "Note \"{}\" not found.".format(note_id)

        if self.core.memorystore.has_note(self, note_id):  # hide
            content = self.core.memorystore.delete_note(self, note_id)
            return "Hide encrypted note content."
        else:  # show
            content = self.core.textfilestore.get_encrypted_note_text(self,
                                                                      note_id,
                                                                      passphrase)
            note = EncryptedNote(note_id, content)
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
                                                                      note.note_id,
                                                                      passphrase)
            note = EncryptedNote(note.note_id, content)
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
        return self.core.memorystore.has_note(self, note.note_id)

    def get_visible_note(self, note):
        return self.core.memorystore.get_note(self, note.note_id)
