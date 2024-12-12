import socket

from httplib2 import ServerNotFoundError

from ctui.google_contacts import GoogleStore
from ctui.handler.contact_handler import ContactHandler
from ctui.keybindings import Keybindings
from ctui.memory import MemoryStore
from ctui.model.contact import Contact
from ctui.model.google_contact import GoogleContact
from ctui.rdf import RDFStore
from ctui.textfile import TextFileStore
from ctui.service.editor import Editor


class Core:
    def __init__(self, config, test=False):
        self.ui = None
        self.current_contact = None
        self.current_contact_pos = None

        self.contact_handler = ContactHandler(self)

        self.rdfstore = RDFStore(config['path']['rdf_file'],
                                 config['rdf']['namespace'])
        self.textfilestore = TextFileStore(config['path']['textfile_dir'],
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

        self.keybindings = Keybindings(config)
        self.editor = Editor(self, config['editor']['editor'])
        self.last_keypress = None

        self.filter_string = ''

    def register_ui(self, ui):
        self.ui = ui

    def is_connected(self):
        """
        Check if connected to the internet
        """
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

    def update_contact_list(self, filter_string=None):
        contact_list = self.contact_handler.load_contacts()
        contact_list = self.apply_filter(contact_list, filter_string)
        self.ui.set_contact_list(contact_list)

    def update_contact_details(self, contact_id):
        # load contact details only when needed, not before for performance
        contact = self.contact_handler.load_details(contact_id)
        self.ui.set_contact_details(contact)

    @staticmethod
    def apply_filter(contact_list, filter_string=None):
        if not filter_string:
            return contact_list

        contacts = []
        for contact in contact_list:
            if filter_string.lower() in contact.name.lower():
                contacts.append(contact)
        contacts.sort(key=lambda x: x.name)
        return contacts

    def select_contact(self, contact_id: str) -> None:
        if self.contains_contact_id(contact_id):
            self.ui.set_focused_contact(contact_id)
            self.update_contact_details(contact_id)
        else:
            name = Contact.id_to_name(contact_id)
            self.ui.console.show_message(f"Contact '{name}' not found")

    def contains_contact(self, contact):
        """
        @deprecated use contains_contact_id
        """
        return self.rdfstore.contains_contact(contact) or \
            self.textfilestore.contains_contact(contact)

    def contains_contact_id(self, name):
        """
        TODO rename to contains_contact()
        """
        return self.rdfstore.contains_contact_id(name) or \
            self.textfilestore.contains_contact_id(name)

    def contains_contact_name(self, name):
        return self.rdfstore.contains_contact_name(name) or \
            self.textfilestore.contains_contact_name(name)

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
        if self.textfilestore.contains_contact(contact):
            self.textfilestore.rename_contact(contact, new_name)
        return "{} renamed to {}.".format(contact.name, new_name)

    def delete_contact(self, contact):
        """
        @deprecated
        """
        return self.delete_contact_by_id(contact.get_id())

    def delete_contact_by_id(self, contact_id):
        name = Contact.id_to_name(contact_id)
        if not self.contains_contact_id(contact_id):
            return "Error: {} doesn't exists.".format(name)
        # if type(contact_id) is GoogleContact:
        #     self.googlestore.delete_contact(contact_id)
        if self.rdfstore.contains_contact_id(contact_id):
            self.rdfstore.delete_contact(contact_id)
        if self.textfilestore.contains_contact_id(contact_id):
            self.textfilestore.delete_contact(contact_id)
        return "{} deleted.".format(name)

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

    def set_contact_filter(self):
        self.filter_string = ''
        command = 'filter {}'.format(self.filter_string)
        self.ui.console.show_filter(command)

    def clear_contact_filter(self):
        self.filter_string = ''
        # TODO show unfiltered contact list
        self.ui.frame.focus_position = 'body'
        self.ui.focus_list_view()
        self.ui.set_focused_contact(None)  # TODO which was the last contact?
