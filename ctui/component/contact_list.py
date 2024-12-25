import urwid
from pyfzf.pyfzf import FzfPrompt

from ctui.component.contact_entry import ContactEntry
from ctui.component.keypress_mixin import KeypressMixin, KeybindingCommand
from ctui.component.list_box import CListBox
from ctui.component.list_entry import CListEntry
from ctui.model.contact import Contact


class ContactList(CListBox, KeypressMixin):
    no_result_msg = "<no result>"

    def __init__(self, core):
        self.core = core
        self.listwalker = urwid.SimpleFocusListWalker([])
        super(ContactList, self).__init__(self.listwalker, core, 'contact_list')

    def set_data(self, contact_list):
        contact_entry_widgets = []
        pos = 0

        is_empty = len(contact_list) == 0

        if is_empty:
            entry = CListEntry(ContactList.no_result_msg, 0, self.core)
            contact_entry_widgets.append(entry)
        else:
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
        contact_id = None

        if hasattr(self.focus, 'contact'):
            contact_id = self.focus.contact.get_id()

        self.core.update_contact_details(contact_id)

    def get_focused_contact(self):
        if hasattr(self.focus, 'contact'):
            return self.focus.contact

    def set_focused_contact(self, contact_id: str) -> None:
        pos = self.get_contact_position(contact_id)
        self.set_focus(pos)

    def get_focused_contact_pos(self) -> int:
        return self.focus_position

    def set_focused_contact_pos(self, pos: int) -> None:
        self.set_focus(pos)

    def get_count(self) -> int:
        return len(self.body)

    def get_contact_position(self, contact_id: str) -> int | None:
        pos = 0
        for entry in self.body:
            if entry.contact.get_id() == contact_id:
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
        return self.handle_keypress(size, key)

    @KeybindingCommand("move_right")
    def move_right(self, command_repeat, size):
        self.core.keybindings.set_simulating(True)
        key = super(ContactList, self).keypress(size, 'right')
        self.core.keybindings.set_simulating(False)
        return key

    @KeybindingCommand("search_contact")
    def search_contact(self, command_repeat, size):
        fzf = FzfPrompt()
        contact_list = self.core.contact_handler.load_contact_names()
        options='--color=hl:red,fg+:#000000,bg+:white,hl+:red,spinner:black,prompt:black,info:grey --pointer="" --marker=""'
        selected = fzf.prompt(contact_list, options)

        if selected:
            contact_name = selected[0]  # fzf returns list
            contact_id = Contact.name_to_id(contact_name)
            self.core.ui.set_focused_contact(contact_id)

        self.core.ui.main_loop.screen.clear()  # redraw screen

    @KeybindingCommand("set_contact_filter")
    def set_contact_filter(self, command_repeat, size):
        self.core.set_contact_filter()

    @KeybindingCommand("clear_contact_filter")
    def clear_contact_filter(self, command_repeat, size):
        self.core.clear_contact_filter()
