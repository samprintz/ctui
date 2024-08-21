import urwid

from ctui.component.contact_entry import ContactEntry
from ctui.component.list_box import CListBox


class ContactList(CListBox):
    def __init__(self, core):
        self.core = core
        self.listwalker = urwid.SimpleFocusListWalker([])
        super(ContactList, self).__init__(self.listwalker, core, 'contact_list')

    def set_data(self, contact_list):
        contact_entry_widgets = []
        pos = 0
        for c in contact_list:
            entry = ContactEntry(c, pos, self.core)
            contact_entry_widgets.append(entry)
            pos = pos + 1

        urwid.disconnect_signal(self.listwalker, 'modified',
                                self.select_contact)

        while len(self.listwalker) > 0:
            self.listwalker.pop()

        self.listwalker.extend(contact_entry_widgets)

        urwid.connect_signal(self.body, 'modified', self.select_contact)

        self.listwalker.set_focus(0)

    def select_contact(self):
        self.core.select_contact(self.focus.contact)

    def get_focused_contact(self):
        return self.focus.contact

    def set_focused_contact(self, contact):
        pos = self.get_contact_position(contact)
        self.set_focus(pos)

    def get_focus_position(self):
        return self.focus_position

    def set_focus_position(self, pos):
        self.focus_position = pos

    def get_contact_position(self, contact):
        pos = 0
        for entry in self.body:
            if entry.label == contact.name:
                return pos
            pos = pos + 1
        return None

    def get_contact_position_startswith(self, name):
        pos = 0
        for entry in self.body:
            if entry.label.lower().startswith(name.lower()):
                return pos
            pos = pos + 1
        return None

    def get_contact_position_contains(self, name):
        pos = 0
        for entry in self.body:
            if name.lower() in entry.label.lower():
                return pos
            pos = pos + 1
        return None

    def jump_to_contact(self, name):
        pos = self.get_contact_position_startswith(name)
        if pos is None:
            pos = self.get_contact_position_contains(name)
        if pos is not None:
            self.set_focus(pos)
            return True
        return False

    def keypress(self, size, key):
        key = super(ContactList, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_right':
                self.core.keybindings.set_simulating(True)
                key = super(ContactList, self).keypress(size, 'right')
                self.core.keybindings.set_simulating(False)
                return key
            case 'search_contact':
                self.core.cli.search_contact()
            case 'set_contact_filter':
                self.core.cli.filter_contacts()
            case 'clear_contact_filter':
                self.core.cli.unfilter_contacts()
            case 'add_google_contact':
                self.core.cli.add_google_contact()
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
