from datetime import date, datetime
from enum import Enum

from ctui.commands import Command, AddAttribute
from ctui.objects import Attribute, Contact, Gift, Note, EncryptedNote


class CLI:
    """
    Vim-like console that serves as main user interface for data-manipulation (esp. create, update, delete).
    """

    def __init__(self, core):
        self.core = core
        self.contact = None
        self.detail = None
        self.filter_string = ''
        self.mode = None
        self.note = None

    def handle(self, args):
        if self.mode is Mode.SEARCH:
            name = " ".join(args[0:])
            msg = self.core.search_contact(name)
            self.mode = None
            self.action = None
            self.core.ui.frame.focus_position = 'body'
            self.core.ui.console.show_message(msg)

        elif self.mode is Mode.FILTER:
            if args is not False:
                filter_string = " ".join(args[1:])
                self.core.filter_string = filter_string
                self.filter_string = filter_string
                self.action = Action.FILTERING
                self.core.ui.refresh_contact_list(self.action, self.contact,
                                                  self.detail,
                                                  self.filter_string)
            else:  # enter was pressed
                self.action = Action.FILTERED
                self.core.ui.refresh_contact_list(self.action, self.contact,
                                                  self.detail,
                                                  self.filter_string)
                self.core.ui.frame.focus_position = 'body'
                msg = 'f={}'.format(self.core.filter_string)
                self.core.ui.frame.console.show_message(msg)
                self.mode = None

        else:
            command = args[0]

            found_in_new_commands = False

            for command_class in Command.__subclasses__():
                if command in command_class.names:
                    command_instance = command_class(self.core)
                    msg = command_instance.execute(args[1:])
                    found_in_new_commands = True

            if not found_in_new_commands:
                if command in ('add-contact'):
                    name = " ".join(args[1:])
                    contact = Contact(name, self.core)
                    msg = self.core.add_contact(contact)
                    self.contact = contact  # to focus it when refreshing contact list
                    self.action = Action.CONTACT_ADDED_OR_EDITED
                elif command in ('rename-contact'):
                    contact = self.contact
                    new_name = " ".join(args[1:])
                    msg = self.core.rename_contact(contact, new_name)
                    contact.name = new_name  # TODO
                    self.contact = contact  # to focus it when refreshing contact list
                    self.action = Action.CONTACT_ADDED_OR_EDITED
                elif command in ('delete-contact'):
                    name = " ".join(args[1:])
                    msg = self.core.delete_contact_by_name(name)
                    self.contact = None  # to focus other when refreshing contact list
                    self.action = Action.CONTACT_DELETED
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
                elif command in ('add-encrypted-note'):
                    date_str = " ".join(args[1:])
                    msg = self.contact.add_encrypted_note(date_str)
                    self.detail = EncryptedNote(date_str, None)
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
                elif command in ('encrypt-note'):
                    date_str = " ".join(args[1:])
                    msg = self.contact.encrypt_note(date_str)
                    self.detail = EncryptedNote(date_str, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('decrypt-note'):
                    date_str = " ".join(args[1:])
                    msg = self.contact.decrypt_note(date_str)
                    self.detail = Note(date_str, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('toggle-note-encryption'):
                    date_str = " ".join(args[1:])
                    msg = self.contact.toggle_note_encryption(date_str)
                    self.detail = EncryptedNote(date_str, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('show-all-encrypted-notes'):
                    msg = self.contact.show_all_encrypted_notes()
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('hide-all-encrypted-notes'):
                    msg = self.contact.hide_all_encrypted_notes()
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('add-google-contact'):
                    name = " ".join(args[1:])
                    contact, msg = self.core.add_google_contact(name)
                    self.contact = contact  # to focus it when refreshing contact list
                    self.action = Action.CONTACT_ADDED_OR_EDITED
                else:
                    msg = 'Not a valid command.'

                self.core.ui.refresh_contact_list(self.action, self.contact,
                                                  self.detail,
                                                  self.filter_string)

            self.core.ui.frame.focus_position = 'body'
            self.core.ui.console.show_message(msg)

    # contacts

    def add_contact(self):
        command = 'add-contact '
        self.core.ui.console.show_console(command)

    def add_google_contact(self):
        command = 'add-google-contact '
        self.core.ui.console.show_console(command)

    def rename_contact(self, contact):
        self.contact = contact
        command = 'rename-contact {}'.format(contact.name)
        self.core.ui.console.show_console(command)

    def delete_contact(self, contact):
        self.contact = contact
        command = 'delete-contact {}'.format(contact.name)
        self.core.ui.console.show_console(command)

    def search_contact(self):
        self.mode = Mode.SEARCH
        self.core.ui.console.show_search()

    def filter_contacts(self):
        self.mode = Mode.FILTER
        if self.core.filter_mode is False:
            self.core.filter_string = ''
        self.core.filter_mode = True
        command = 'filter {}'.format(self.core.filter_string)
        self.core.ui.console.show_filter(command)

    def unfilter_contacts(self):
        self.mode = None
        self.action = Action.FILTERED
        self.filter_string = ''
        self.core.filter_mode = False
        self.core.filter_string = ''
        self.core.ui.refresh_contact_list(self.action, self.contact,
                                          self.detail, self.filter_string)
        self.core.ui.console.clear()
        self.core.ui.frame.focus_position = 'body'

    # gifts

    def edit_gift(self, contact, gift):
        self.contact = contact
        self.detail = gift
        command = 'edit-gift {}'.format(gift.name)
        self.core.ui.console.show_console(command)

    def delete_gift(self, contact, gift):
        self.contact = contact
        self.detail = gift
        command = 'delete-gift {}'.format(gift.name)
        self.core.ui.console.show_console(command)

    def mark_gifted(self, contact, gift):
        self.contact = contact
        self.detail = gift
        new_name = "x " + gift.name[2:]
        command = 'edit-gift {}'.format(new_name)
        self.core.ui.console.show_console(command)

    def unmark_gifted(self, contact, gift):
        self.contact = contact
        self.detail = gift
        new_name = gift.name[2:]
        command = 'edit-gift {}'.format(new_name)
        self.core.ui.console.show_console(command)

    # notes

    def add_note(self, contact):
        self.contact = contact
        date_str = datetime.strftime(date.today(), "%Y%m%d")
        command = 'add-note {}'.format(date_str)
        self.core.ui.console.show_console(command)

    def add_encrypted_note(self, contact):
        self.contact = contact
        date_str = datetime.strftime(date.today(), "%Y%m%d")
        command = 'add-encrypted-note {}'.format(date_str)
        self.core.ui.console.show_console(command)

    def rename_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        command = 'rename-note {}'.format(date_str)
        self.core.ui.console.show_console(command)

    def delete_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        command = 'delete-note {}'.format(date_str)
        self.core.ui.console.show_console(command)

    def edit_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        args = 'edit-note {}'.format(date_str).split()
        self.core.cli.handle(args)

    def encrypt_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        args = 'encrypt-note {}'.format(date_str).split()
        self.core.cli.handle(args)

    def decrypt_note(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        args = 'decrypt-note {}'.format(date_str).split()
        self.core.cli.handle(args)

    def toggle_note_encryption(self, contact, note):
        self.contact = contact
        self.detail = note
        date_str = datetime.strftime(note.date, "%Y%m%d")
        args = 'toggle-note-encryption {}'.format(date_str).split()
        self.core.cli.handle(args)

    def show_all_encrypted_notes(self, contact):
        self.contact = contact
        args = ['show-all-encrypted-notes']
        self.core.cli.handle(args)

    def hide_all_encrypted_notes(self, contact):
        self.contact = contact
        args = ['hide-all-encrypted-notes']
        self.core.cli.handle(args)


class Mode(Enum):
    SEARCH = 'search'
    FILTER = 'filter'
    CONSOLE = 'console'
    INPUT = 'input'


class Action(Enum):
    REFRESH = 'refresh'
    CONTACT_ADDED_OR_EDITED = 'contact_added_or_edited'
    CONTACT_DELETED = 'contact_deleted'
    DETAIL_ADDED_OR_EDITED = 'detail_added_or_edited'
    DETAIL_DELETED = 'detail_deleted'
    FILTERING = 'filtering'  # when the console is still open
    FILTERED = 'filtered'  # when filter string is entered and the console closed
