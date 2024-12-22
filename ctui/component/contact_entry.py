import urwid

from ctui.component.list_entry import CListEntry


class ContactEntry(CListEntry):
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

        key = super(ContactEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def rename_contact(command_repeat, size):
            command = f'rename-contact {self.contact.name}'
            self.core.ui.console.show_console(command)

        def delete_contact(command_repeat, size):
            command = f'delete-contact {self.contact.name}'
            self.core.ui.console.show_console(command)

        return {
            'rename_contact': rename_contact,
            'delete_contact': delete_contact,
        }
