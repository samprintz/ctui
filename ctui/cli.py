from datetime import date, datetime
from enum import Enum

from ctui.commands import Command
from ctui.objects import Gift, Note, EncryptedNote


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
                self.core.ui.console.show_message(msg)
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
                if command in ('edit-gift'):
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
                    note_id = " ".join(args[1:])
                    msg = self.contact.add_note(note_id)
                    self.detail = Note(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('add-encrypted-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.add_encrypted_note(note_id)
                    self.detail = EncryptedNote(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('rename-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.rename_note(self.detail, note_id)
                    self.detail = Note(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('delete-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.delete_note(note_id)
                    self.action = Action.DETAIL_DELETED
                elif command in ('edit-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.edit_note(note_id)
                    self.detail = Note(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('encrypt-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.encrypt_note(note_id)
                    self.detail = EncryptedNote(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('decrypt-note'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.decrypt_note(note_id)
                    self.detail = Note(note_id, None)
                    self.action = Action.DETAIL_ADDED_OR_EDITED
                elif command in ('toggle-note-encryption'):
                    note_id = " ".join(args[1:])
                    msg = self.contact.toggle_note_encryption(note_id)
                    self.detail = EncryptedNote(note_id, None)
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

    def add_google_contact(self):
        command = 'add-google-contact '
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

    # notes

    def add_note(self, contact):
        self.contact = contact
        note_id = datetime.strftime(date.today(), "%Y%m%d")
        command = 'add-note {}'.format(note_id)
        self.core.ui.console.show_console(command)

    def add_encrypted_note(self, contact):
        self.contact = contact
        note_id = datetime.strftime(date.today(), "%Y%m%d")
        command = 'add-encrypted-note {}'.format(note_id)
        self.core.ui.console.show_console(command)

    def rename_note(self, contact, note):
        self.contact = contact
        self.detail = note
        command = 'rename-note {}'.format(note.note_id)
        self.core.ui.console.show_console(command)

    def delete_note(self, contact, note):
        self.contact = contact
        self.detail = note
        command = 'delete-note {}'.format(note.note_id)
        self.core.ui.console.show_console(command)

    def edit_note(self, contact, note):
        self.contact = contact
        self.detail = note
        args = 'edit-note {}'.format(note.note_id).split()
        self.core.cli.handle(args)

    def encrypt_note(self, contact, note):
        self.contact = contact
        self.detail = note
        args = 'encrypt-note {}'.format(note.note_id).split()
        self.core.cli.handle(args)

    def decrypt_note(self, contact, note):
        self.contact = contact
        self.detail = note
        args = 'decrypt-note {}'.format(note.note_id).split()
        self.core.cli.handle(args)

    def toggle_note_encryption(self, contact, note):
        self.contact = contact
        self.detail = note
        args = 'toggle-note-encryption {}'.format(note.note_id).split()
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
