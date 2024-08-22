import urwid

from ctui.component.contact_details import GeneralDetails, GiftDetails, \
    NoteDetails


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
        self.tab_content = {
            'General': GeneralDetails(contact, self.core),
            'Gifts': GiftDetails(contact, self.core),
            'Notes': NoteDetails(contact, self.core)
        }

        self.header = CDetailTabNavigation(['General', 'Gifts', 'Notes'],
                                           self.on_tab_click)

        self.body = CDetailTabBody(self.tab_content['General'])
