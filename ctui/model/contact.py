import os

from ctui.model.encrypted_note import EncryptedNote
from ctui.model.gift import Gift
from ctui.model.note import Note


class Contact:

    def __init__(self, name, core, attributes=None, gifts=None, notes=None):
        self.name = name

        # TODO Contact shouldn't have core
        self.core = core

        # TODO rebuild as model class, not as business layer
        # but where to put the business logic?
        # self.core.has_contact_attribute(contact, attribute)
        # self.core.add_detail_to_contact(contact, detail)

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
            self.core.textfilestore.has_gifts(self.get_id()) or \
            self.core.textfilestore.has_notes(self.get_id())

    def load_details(self):
        self.attributes = self.core.rdfstore.get_attributes(self)
        self.gifts = self.core.textfilestore.get_gifts(self.get_id())
        self.notes = self.core.textfilestore.get_notes(self.get_id())

    # notes

    def get_notes_path(self):
        return self.core.textfilestore.get_textfile_path_by_type(self.get_id(),
                                                                 self.core.textfilestore.NOTES_DIR)

    def get_gifts_path(self):
        return self.core.textfilestore.get_textfile_path_by_type(self.get_id(),
                                                                 self.core.textfilestore.GIFTS_DIR)

    def has_note(self, note_id):
        return self.core.textfilestore.has_note(self.get_id(), note_id)

    # memory

    def has_visible_note(self, note):
        return self.core.memorystore.has_note(self.get_id(), note.note_id)

    def get_visible_note(self, note):
        return self.core.memorystore.get_note(self.get_id(), note.note_id)
