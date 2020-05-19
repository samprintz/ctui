from objects import *
import core
import pudb

"""
Vim-like console that serves as main user interface for data-manipulation (esp. create, update, delete).
"""
class CLI:
    def __init__(self, core):
        self.core = core


    def handle(self, args):
        command = args[0]
        if command in ('add-contact'):
            name = " ".join(args[1:])
            contact = Contact(name, self.core)
            msg = self.core.add_contact(contact)
            self.contact = contact # to focus it when refreshing contact list
        elif command in ('rename-contact'):
            contact = self.contact
            new_name = " ".join(args[1:])
            msg = self.core.rename_contact(contact, new_name)
            contact.name = new_name # TODO
            self.contact = contact # to focus it when refreshing contact list
        elif command in ('delete-contact'):
            name = " ".join(args[1:])
            contact = Contact(name, self.core)
            msg = self.core.delete_contact(contact)
            self.contact = None # to focus other when refreshing contact list
        elif command in ('add-attribute'):
            key = args[1]
            value = " ".join(args[2:])
            attribute = Attribute(key, value)
            msg = self.contact.add_attribute(attribute)
        elif command in ('edit-attribute'):
            key = args[1]
            value = " ".join(args[2:])
            new_attr = Attribute(key, value)
            old_attr = self.attribute
            msg = self.contact.edit_attribute(old_attr, new_attr)
        elif command in ('delete-attribute'):
            key = args[1]
            value = " ".join(args[2:])
            attribute = Attribute(key, value)
            msg = self.contact.delete_attribute(attribute)
        else:
            msg = 'Not a valid command.'

        self.core.frame.refresh_contact_list(self.contact, self.pos)
        self.core.frame.set_focus('body')
        self.core.frame.console.show_message(msg)


    # contacts

    def add_contact(self, pos):
        self.pos = pos
        command = 'add-contact '
        self.core.frame.console.show_console(command)

    def rename_contact(self, contact, pos):
        self.contact = contact
        self.pos = pos
        command = 'rename-contact {}'.format(contact.name)
        self.core.frame.console.show_console(command)

    def delete_contact(self, contact, pos):
        self.contact = contact
        self.pos = pos
        command = 'rename-contact {}'.format(contact.name)
        command = 'delete-contact {}'.format(contact.name)
        self.core.frame.console.show_console(command)

    # attributes

    def add_attribute(self, contact):
        self.contact = contact
        command = 'add-attribute '
        self.core.frame.console.show_console(command)

    def edit_attribute(self, contact, attribute):
        self.contact = contact
        self.attribute = attribute
        command = 'edit-attribute {} {}'.format(attribute.key, attribute.value)
        self.core.frame.console.show_console(command)

    def delete_attribute(self, contact, attribute):
        self.contact = contact
        self.attribute = attribute
        command = 'delete-attribute {} {}'.format(attribute.key, attribute.value)
        self.core.frame.console.show_console(command)

    # gifts

    def add_gift(contact, gift):
        pass

    def edit_gift(contact, gift):
        pass

    def delete_gift(contact, gift):
        pass

    def mark_gifted(contact, gift):
        pass

    def unmark_gifted(contact, gift):
        pass

    # notes

    def add_note(contact, note):
        pass

    def delete_note(contact, note):
        pass

    def edit_note(contact, note):
        pass

