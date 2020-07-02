from datetime import date,datetime
from enum import Enum
import pudb #TODO

import core
from objects import *


"""
Vim-like console that serves as main user interface for data-manipulation (esp. create, update, delete).
"""
class CLI:
    def __init__(self, core):
        self.core = core
        self.contact = None
        self.detail = None
        self.mode = None


    def handle(self, args):
        if self.mode is Mode.SEARCH:
            name = " ".join(args[0:])
            msg = self.core.search_contact(name)
            self.mode = None
            self.action = None

        else:
            command = args[0]
            if command in ('add-contact'):
                name = " ".join(args[1:])
                contact = Contact(name, self.core)
                msg = self.core.add_contact(contact)
                self.contact = contact # to focus it when refreshing contact list
                self.action = Action.CONTACT_ADDED_OR_EDITED
            elif command in ('rename-contact'):
                contact = self.contact
                new_name = " ".join(args[1:])
                msg = self.core.rename_contact(contact, new_name)
                contact.name = new_name # TODO
                self.contact = contact # to focus it when refreshing contact list
                self.action = Action.CONTACT_ADDED_OR_EDITED
            elif command in ('delete-contact'):
                name = " ".join(args[1:])
                contact = Contact(name, self.core)
                msg = self.core.delete_contact(contact)
                self.contact = None # to focus other when refreshing contact list
                self.action = Action.CONTACT_DELETED
            elif command in ('add-attribute'):
                key = args[1]
                value = " ".join(args[2:])
                attribute = Attribute(key, value)
                msg = self.contact.add_attribute(attribute)
                self.detail = attribute
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('edit-attribute'):
                key = args[1]
                value = " ".join(args[2:])
                new_attr = Attribute(key, value)
                old_attr = self.detail
                msg = self.contact.edit_attribute(old_attr, new_attr)
                self.detail = new_attr
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('delete-attribute'):
                key = args[1]
                value = " ".join(args[2:])
                attribute = Attribute(key, value)
                msg = self.contact.delete_attribute(attribute)
                self.action = Action.DETAIL_DELETED
            elif command in ('add-gift'):
                name = " ".join(args[1:])
                gift = Gift(name)
                msg = self.contact.add_gift(gift)
                self.detail = gift
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('edit-gift'):
                name = " ".join(args[1:])
                new_gift = Gift(name)
                old_gift = self.detail
                msg = self.contact.edit_gift(old_gift, new_gift)
                self.detail = new_gift
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('delete-gift'):
                name = " ".join(args[1:])
                gift = Gift(name)
                msg = self.contact.delete_gift(gift)
                self.action = Action.DETAIL_DELETED
            elif command in ('add-note'):
                date_str = " ".join(args[1:])
                msg = self.contact.add_note(date_str)
                self.detail = Note(date_str, None)
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('rename-note'):
                date_str = " ".join(args[1:])
                msg = self.contact.rename_note(self.detail, date_str)
                self.detail = Note(date_str, None)
                self.action = Action.DETAIL_ADDED_OR_EDITED
            elif command in ('delete-note'):
                date_str = " ".join(args[1:])
                msg = self.contact.delete_note(date_str)
                self.action = Action.DETAIL_DELETED
            elif command in ('edit-note'):
                date_str = " ".join(args[1:])
                msg = self.contact.edit_note(date_str)
                self.detail = Note(date_str, None)
                self.action = Action.DETAIL_ADDED_OR_EDITED
            else:
                msg = 'Not a valid command.'

            self.core.frame.refresh_contact_list(self.action, self.contact, self.detail)

        self.core.frame.set_focus('body')
        self.core.frame.console.show_message(msg)


    # contacts

    def add_contact(self):
        command = 'add-contact '
        self.core.frame.console.show_console(command)

    def rename_contact(self, contact):
        self.contact = contact
        command = 'rename-contact {}'.format(contact.name)
        self.core.frame.console.show_console(command)

    def delete_contact(self, contact):
        self.contact = contact
        command = 'delete-contact {}'.format(contact.name)
        self.core.frame.console.show_console(command)

    def search_contact(self):
        self.mode = Mode.SEARCH
        self.core.frame.console.show_search()

    # attributes

    def add_attribute(self, contact):
        self.contact = contact
        command = 'add-attribute '
        self.core.frame.console.show_console(command)

    def edit_attribute(self, contact, attribute):
        self.contact = contact
        self.detail = attribute
        command = 'edit-attribute {} {}'.format(attribute.key, attribute.value)
        self.core.frame.console.show_console(command)

    def delete_attribute(self, contact, attribute):
        self.contact = contact
        self.detail = attribute
        command = 'delete-attribute {} {}'.format(attribute.key, attribute.value)
        self.core.frame.console.show_console(command)

    # gifts

    def add_gift(self, contact):
        self.contact = contact
        command = 'add-gift '
        self.core.frame.console.show_console(command)

    def edit_gift(self, contact, gift):
        self.contact = contact
        self.detail = gift
        command = 'edit-gift {}'.format(gift.name)
        self.core.frame.console.show_console(command)

    def delete_gift(self, contact, gift):
        self.contact = contact
        self.detail = gift
        command = 'delete-gift {}'.format(gift.name)
        self.core.frame.console.show_console(command)

    def mark_gifted(self, contact, gift):
        self.contact = contact
        self.detail = gift
        new_name = "x " + gift.name[2:]
        command = 'edit-gift {}'.format(new_name)
        self.core.frame.console.show_console(command)

    def unmark_gifted(self, contact, gift):
        self.contact = contact
        self.detail = gift
        new_name = gift.name[2:]
        command = 'edit-gift {}'.format(new_name)
        self.core.frame.console.show_console(command)

    # notes

    def add_note(self, contact):
        self.contact = contact
        date_str = datetime.strftime(date.today(), "%Y%m%d")
        command = 'add-note {}'.format(date_str)
        self.core.frame.console.show_console(command)

    def rename_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        command = 'rename-note {}'.format(date_str)
        self.core.frame.console.show_console(command)

    def delete_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        command = 'delete-note {}'.format(date_str)
        self.core.frame.console.show_console(command)

    def edit_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        args = 'edit-note {}'.format(date_str).split()
        self.core.cli.handle(args)



class Mode(Enum):
    SEARCH = 'search'
    CONSOLE = 'console'
    INPUT = 'input'

class Action(Enum):
    CONTACT_ADDED_OR_EDITED = 'contact_added_or_edited'
    CONTACT_DELETED = 'contact_deleted'
    DETAIL_ADDED_OR_EDITED = 'detail_added_or_edited'
    DETAIL_DELETED = 'detail_deleted'

