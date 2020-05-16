import notes
import rdf
import tui

from datetime import date,datetime
from subprocess import call
import operator
import os
import pudb
import pyperclip
import shutil


"""
Business logic of the contact TUI.
"""
class Core:

    def __init__(self, config):
        self.rdfstore = rdf.RDFStore(config['path']['rdf_file'])
        self.notesstore = notes.NotesStore(config['path']['notes_dir'])
        contacts = self.get_all_contacts()

        self.frame = tui.ContactFrame(config, self)
        self.frame.set_contact_list(contacts)
        loop = tui.ContactLoop(self.frame, config)

    """
    Returns a list of all contacts without their details.
    """
    def get_all_contacts(self):
        contact_names = self.rdfstore.get_all_contact_names() \
                + self.notesstore.get_all_contact_names()
        sorted_contact_names = sorted(set(contact_names))
        contacts = []
        for c in sorted_contact_names:
            contacts.append(Contact(c, self))
        return contacts 

    """
    Returns a list of the names of all contacts.
    """
    def get_all_contact_names(self):
        contact_names = self.rdfstore.get_all_contact_names() \
                + self.notesstore.get_all_contact_names()
        return sorted(set(contact_names))

    def get_contact(name):
        pass

    def add_contact(contact):
        pass

    def rename_contact(contact, new_name):
        pass

    def delete_contact(contact):
        pass


class Contact:

    def __init__(self, name, core, attributes=None, gifts=None, notes=None):
        self.name = name
        self.core = core
        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_details(self):
        self.attributes = self.get_attributes()
        self.gifts = self.get_gifts()
        self.notes = self.get_notes()

    # attributes

    def get_attributes(self):
        return self.core.rdfstore.get_attributes(self)

    def add_attribute(self, attribute):
        pass

    def edit_attribute(self, old_attr, new_attr):
        pass

    def delete_attribute(self, attribute):
        pass

    # gifts

    def get_gifts(self):
        return self.core.rdfstore.get_gifts(self)

    def add_gift(self, gift):
        pass

    def edit_gift(self, gift):
        pass

    def delete_gift(self, gift):
        pass

    def mark_gifted(self, gift):
        pass

    def unmark_gifted(self, gift):
        pass

    # notes

    def get_notes(self):
        return self.core.notesstore.get_notes(self)

    def add_note(self, note):
        pass

    def delete_note(self, note):
        pass

    def edit_note(self, note):
        pass

