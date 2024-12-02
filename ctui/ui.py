import urwid

from ctui.component.console import Console
from ctui.component.contact_details_frame import CDetailsFrame
from ctui.component.contact_frame import CFrame
from ctui.component.contact_frame_columns import CFrameColumns
from ctui.component.contact_list import ContactList


class UI:
    def __init__(self, core, config):
        self.core = core
        self.core.register_ui(self)
        self.name = 'frame'

        palette = [('selected', '', 'light gray')]

        self.list_view = ContactList(core)
        self.detail_view = CDetailsFrame(core, config)

        frame_columns = CFrameColumns(self.list_view, self.detail_view, core,
                                      config)

        self.console = Console(self.core)
        frame_footer = urwid.BoxAdapter(self.console, height=1)

        self.frame = CFrame(frame_columns, frame_footer, core, config)
        self.main_loop = urwid.MainLoop(self.frame, palette)

    def run(self):
        self.set_contact_list(self.core.get_all_contacts())  # TODO remove
        self.main_loop.run()

    def is_focus_on_details(self):
        return self.frame.body.focus_position == 1

    def set_contact_list(self, contact_list):
        self.list_view.set_data(contact_list)

    def set_contact_details(self, contact):
        self.detail_view.set_contact(contact)

    def focus_list_view(self):
        self.frame.body.focus_position = 0

    def focus_detail_view(self):
        self.frame.body.focus_position = 1

    def get_focused_tab(self):
        pass  # TODO

    def set_focused_tab(self):
        pass  # TODO

    def get_focused_contact(self):
        return self.list_view.get_focused_contact()

    def set_focused_contact(self, contact):
        self.list_view.set_focused_contact(contact)

    def get_focused_contact_pos(self):
        return self.list_view.get_focused_contact_pos()

    def set_focused_contact_pos(self, contact):
        self.list_view.set_focused_contact_pos(contact)

    def get_focused_detail(self):
        return self.detail_view.get_focused_detail()

    def set_focused_detail(self, detail):
        self.detail_view.set_focused_detail(detail)

    def get_focused_detail_pos(self):
        return self.detail_view.get_focused_detail_pos()

    def set_focused_detail_pos(self, detail_pos):
        self.detail_view.set_focused_detail_pos(detail_pos)
