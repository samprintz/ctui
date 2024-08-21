import urwid

from ctui.component.list_entry import CListEntry


class ContactEntry(CListEntry):
    def __init__(self, contact, pos, core):
        super(ContactEntry, self).__init__(contact.name, pos, core)
        self.name = 'contact_entry'
        self.contact = contact

        urwid.connect_signal(self, 'click', self.select)

    def select(self, entry):
        self.core.select_contact(entry.contact)

    def keypress(self, size, key):
        if key == 'enter':
            self.core.keybindings.set_simulating(True)
            key = super(ContactEntry, self).keypress(size, 'right')
            self.core.keybindings.set_simulating(False)
            return key

        key = super(ContactEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'rename_contact':
                self.core.cli.rename_contact(self.contact)
            case 'delete_contact':
                self.core.cli.delete_contact(self.contact)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
