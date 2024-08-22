import urwid

from ctui.component.contact_details import ContactDetails


class ContactListBox(urwid.ListBox):
    def __init__(self, items):
        body = urwid.SimpleFocusListWalker([urwid.Text(item) for item in items])
        super().__init__(body)


class CDetailTabNavigation(urwid.Columns):
    def __init__(self, tab_names, callback):
        self.buttons = [urwid.Button(name, on_press=callback, user_data=name)
                        for name in tab_names]
        super().__init__(self.buttons)


class CDetailTabBody(urwid.WidgetPlaceholder):
    def __init__(self, initial_widget):
        super().__init__(initial_widget)


class CDetailsFrame(urwid.Frame):
    def __init__(self, core, config):
        self.core = core
        self.name = 'details_frame'
        super(CDetailsFrame, self).__init__(None)
        self.tab_content = {}

    def on_tab_click(self, button, tab_name):
        self.body.original_widget = self.tab_content[tab_name]

    def set_contact(self, contact):
        general_list = ContactDetails(self.core)
        general_list.set(contact)

        gifts_list = ContactListBox(
            ["Gift item 1", "Gift item 2", "Gift item 3"])
        notes_list = ContactListBox(
            ["Note item 1", "Note item 2", "Note item 3"])

        self.tab_content = {
            'General': general_list,
            'Gifts': gifts_list,
            'Notes': notes_list
        }

        self.header = CDetailTabNavigation(['General', 'Gifts', 'Notes'],
                                           self.on_tab_click)

        self.body = CDetailTabBody(general_list)
