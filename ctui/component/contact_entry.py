import urwid

from ctui.component.keypress_mixin import KeybindingCommand, KeypressMixin
from ctui.component.list_entry import CListEntry


class ContactEntry(CListEntry, KeypressMixin):
    def __init__(self, contact, pos, core):
        super(ContactEntry, self).__init__(contact.name, pos, core)
        self.name = 'contact_entry'
        self.contact = contact

        urwid.connect_signal(self, 'click', self.select)

    def select(self, entry):
        self.core.update_contact_details(entry.contact_id)

    def keypress(self, size, key):
        if key == 'enter':
            self.core.keybindings.set_simulating(True)
            key = super(ContactEntry, self).keypress(size, 'right')
            self.core.keybindings.set_simulating(False)
            return key

        return self.handle_keypress(size, key)

    @KeybindingCommand("rename_contact")
    def rename_contact(self, command_repeat, size):
        command = f'rename-contact {self.contact.name}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("delete_contact")
    def delete_contact(self, command_repeat, size):
        command = f'delete-contact {self.contact.name}'
        self.core.ui.console.show_console(command)
