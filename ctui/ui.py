import urwid

from ctui.component.contact_frame import CFrame
from ctui.component.console import Console
from ctui.component.contact_frame_columns import CFrameColumns

from ctui.component.contact_details_frame import CDetailsFrame
from ctui.component.contact_list import ContactList


class UI:
    def __init__(self, core, config):
        self.core = core
        self.core.register_ui(self)

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
        self.set_contact_list(self.core.get_all_contacts())
        self.main_loop.run()

    def set_contact_list(self, contact_list):
        self.list_view.set_data(contact_list)

    def set_contact_details(self, contact):
        self.detail_view.set_contact(contact)
