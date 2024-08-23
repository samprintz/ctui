import os
import socket
from subprocess import call

from httplib2 import ServerNotFoundError

from ctui.cli import CLI
from ctui.google_contacts import GoogleStore
from ctui.keybindings import Keybindings
from ctui.memory import MemoryStore
from ctui.notes import NotesStore
from ctui.objects import *
from ctui.rdf import RDFStore


class Core:
    def __init__(self, config, test=False):
        self.ui = None
        self.current_contact = None
        self.current_contact_pos = None

        self.rdfstore = RDFStore(config['path']['rdf_file'],
                                 config['rdf']['namespace'])
        self.notesstore = NotesStore(config['path']['notes_dir'],
                                     config['encryption']['keyid'])
        self.memorystore = MemoryStore()

        if False and self.is_connected() and not test:  # TODO
            try:
                self.googlestore = GoogleStore(self, config['google'][
                    'credentials_file'], config['google']['token_file'])
            except ServerNotFoundError:
                self.googlestore = None
        else:
            self.googlestore = None

        self.cli = CLI(self)
        self.keybindings = Keybindings(config)
        self.editor = Editor(config['editor']['editor'])
        self.last_keypress = None

        self.contact_list = self.get_all_contacts()

        self.filter_string = ''

    def register_ui(self, ui):
        self.ui = ui

    """
    Check if connected to the internet
    """

    def is_connected(self):
        hostname = "one.one.one.one"
        try:
            # host name resolvable -> DNS listening
            host = socket.gethostbyname(hostname)
            # connect to the host -> host reachable
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True
        except:
            pass
        return False

    """
    Returns a list of all contacts without their details.
    """

    def get_all_contacts(self):
        contacts = []
        for c in self.rdfstore.get_all_contact_names():
            contacts.append(Contact(c, self))
        for c in self.notesstore.get_all_contact_names():
            # check if contact already in list
            try:
                existing_contact = next(x for x in contacts if c == x.name)
            except StopIteration:
                contacts.append(Contact(c, self))
        if self.googlestore is not None:
            for contact in self.googlestore.get_all_contacts():
                # check if contact already in list
                try:
                    existing_contact = next(
                        x for x in contacts if contact.name == x.name)
                    contacts.remove(existing_contact)
                    contact.merge(existing_contact)
                except StopIteration:
                    pass
                contacts.append(contact)
        contacts.sort(key=lambda x: x.name)
        return contacts

    def get_filtered_contacts(self, filter_string):
        if not filter_string:  # shortcut for empty filter (unfilter)
            return self.contact_list
        contacts = []
        for contact in self.contact_list:
            if filter_string.lower() in contact.name.lower():
                contacts.append(contact)
        contacts.sort(key=lambda x: x.name)
        return contacts

    """
    Returns a list of the names of all contacts.
    """

    def get_all_contact_names(self):
        contact_names = self.rdfstore.get_all_contact_names() \
                        + self.notesstore.get_all_contact_names()

        if self.googlestore is not None:
            contact_names + self.googlestore.get_all_contact_names()

        return sorted(set(contact_names))

    def contains_contact(self, contact):
        return self.rdfstore.contains_contact(contact) or \
            self.notesstore.contains_contact(contact)

    def contains_contact_name(self, name):
        return self.rdfstore.contains_contact_name(name) or \
            self.notesstore.contains_contact_name(name)

    def get_contact(self, name):
        for contact in self.contact_list:
            if contact.name == name:
                return contact

    def select_contact(self, contact):
        self.ui.set_contact_details(contact)

    def search_contact(self, name):
        self.ui.list_view.jump_to_contact(name)
        return ""

    def add_contact(self, contact):
        if self.contains_contact(contact):
            return "Error: {} already exists.".format(contact.name)
        self.rdfstore.add_contact(contact)
        return "{} added.".format(contact.name)

    def rename_contact(self, contact, new_name):
        if not self.contains_contact(contact):
            return "Error: {} doesn't exist.".format(contact.name)
        if contact.name == new_name:
            return "Warning: Name unchanged."
        if self.contains_contact_name(new_name):
            return "Error: {} already exists.".format(new_name)
        if self.rdfstore.contains_contact(contact):
            self.rdfstore.rename_contact(contact, new_name)
        if self.notesstore.contains_contact(contact):
            self.notesstore.rename_contact(contact, new_name)
        return "{} renamed to {}.".format(contact.name, new_name)

    def delete_contact_by_name(self, name):
        contact = self.get_contact(name)
        if contact is None:
            return "Error: {} doesn't exists.".format(name)
        else:
            return self.delete_contact(contact)

    def delete_contact(self, contact):
        if not self.contains_contact(contact):
            return "Error: {} doesn't exists.".format(contact.name)
        if type(contact) is GoogleContact:
            self.googlestore.delete_contact(contact)
        if self.rdfstore.contains_contact(contact):
            self.rdfstore.delete_contact(contact)
        if self.notesstore.contains_contact(contact):
            self.notesstore.delete_contact(contact)
        return "{} deleted.".format(contact.name)

    def add_google_contact(self, name):
        # TODO Check if already exists (offline, not in Google)
        names = name.split()
        givenName = names[0]
        familyName = names[1] if len(names) > 1 else ''
        contact = {"names": [{
            "givenName": givenName,
            "familyName": familyName
        }]}
        self.googlestore.add_contact(contact)
        # GoogleContact object is not the one required by the google API but for the TUI
        google_contact = GoogleContact(name, self)
        return google_contact, "{} added.".format(name)

    def set_filter_string(self, filter_string):
        self.filter_string = filter_string

    def get_filter_string(self):
        return self.filter_string


class Editor:
    def __init__(self, editor_name):
        self.editor = os.environ.get('EDITOR', editor_name)

    def add(self, dirname, filename):
        path = dirname + '/' + filename + '.txt'
        temp_path = path + '.tmp'

        try:
            with open(temp_path, 'w') as tf:
                call([self.editor, tf.name])

            with open(temp_path, 'r') as tf:
                content = tf.read()

            os.remove(temp_path)

        except OSError:
            raise OSError  # TODO

        return content

    def edit(self, dirname, filename):
        path = dirname + '/' + filename + '.txt'
        temp_path = path + '.tmp'

        try:
            with open(path) as f:
                old_content = f.read()

            with open(temp_path, 'w') as tf:
                tf.write(old_content)
                tf.flush()
                call([self.editor, tf.name])

            with open(temp_path, 'r') as tf:
                content = tf.read()

            os.remove(temp_path)
        #            with tempfile.NamedTemporaryFile(
        #                    suffix=".tmp", prefix=filename + '_', dir=dirname) as tf:
        #                tf.write(old_content)
        #                tf.flush()
        #                call([self.editor, tf.name])
        #                tf.seek(0)
        #                content = tf.read().decode("utf-8")

        except OSError:
            raise OSError  # TODO

        return content
