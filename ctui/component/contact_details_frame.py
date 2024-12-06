import urwid

from ctui.component.contact_details import GeneralDetails, GiftDetails, \
    NoteDetails


class CDetailTabNavigation(urwid.Columns):
    def __init__(self, tab_names, callback):
        self.buttons = [
            CTabButton(name, on_press=callback, user_data=name)
            for name in tab_names
        ]
        super().__init__(self.buttons)


class CTabButton(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")


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

    def get_tab_body(self):
        return self.body.original_widget

    def get_focused_detail(self):
        return self.get_tab_body().get_focused_detail()

    def set_focused_detail(self, detail):
        detail_pos = self.get_tab_body().get_detail_position(detail)
        self.set_focused_detail_pos(detail_pos)

    def get_focused_detail_pos(self):
        return self.get_tab_body().get_focus_position()

    def set_focused_detail_pos(self, detail_pos):
        self.get_tab_body().set_focus_position(detail_pos)
