from typing import Union

import urwid

from ctui.component.console import Console
from ctui.component.contact_details_frame import CDetailsFrame
from ctui.component.contact_frame import CFrame
from ctui.component.contact_frame_columns import CFrameColumns
from ctui.component.contact_list import ContactList
from ctui.model.attribute import Attribute
from ctui.model.contact import Contact
from ctui.model.gift import Gift
from ctui.model.note import Note


class UI:
    def __init__(self, core, config):
        self.core = core
        self.core.register_ui(self)
        self.name = 'frame'

        palette = [
            ('selected', '', 'white')
        ]

        self.list_view = ContactList(core)
        self.detail_view = CDetailsFrame(core, config)
        frame_columns = CFrameColumns(self.list_view, self.detail_view, core,
                                      config)
        self.console = Console(self.core)
        frame_footer = urwid.BoxAdapter(self.console, height=1)
        self.frame = CFrame(frame_columns, frame_footer, core, config)

        self.core.update_contact_list()

        self.main_loop = urwid.MainLoop(self.frame, palette)

    def run(self) -> None:
        self.main_loop.run()

    def is_focus_on_details(self) -> bool:
        return self.frame.body.focus_position == 1

    def set_contact_list(self, contact_list) -> None:
        self.list_view.set_data(contact_list)

    def set_contact_details(self, contact_id: str) -> None:
        self.detail_view.set_contact(contact_id)

    def focus_list_view(self) -> None:
        self.frame.body.focus_position = 0

    def focus_detail_view(self) -> None:
        self.frame.body.focus_position = 1

    def get_focused_contact(self) -> Contact:
        return self.list_view.get_focused_contact()

    def set_focused_contact(self, contact_id: str) -> None:
        self.list_view.set_focused_contact(contact_id)

    def get_focused_contact_pos(self) -> int:
        return self.list_view.get_focused_contact_pos()

    def set_focused_contact_pos(self, pos: int) -> None:
        self.list_view.set_focused_contact_pos(pos)

    def get_current_tab(self) -> int:
        return self.detail_view.get_tab()

    def set_current_tab(self, tab: int) -> None:
        self.detail_view.set_tab(tab)

    def next_tab(self) -> None:
        self.detail_view.next_tab()

    def previous_tab(self) -> None:
        self.detail_view.previous_tab()

    def get_focused_detail(self) -> Union[Attribute, Note, Gift]:
        return self.detail_view.get_focused_detail()

    def set_focused_detail(self, detail: Union[Attribute, Note, Gift]) -> None:
        self.detail_view.set_focused_detail(detail)

    def get_focused_detail_pos(self) -> int:
        return self.detail_view.get_focused_detail_pos()

    def set_focused_detail_pos(self, detail_pos: int) -> None:
        self.detail_view.set_focused_detail_pos(detail_pos)
