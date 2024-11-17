import urwid

from ctui.cli import Action
from ctui.component.contact_frame import CFrame
from ctui.component.console import Console
from ctui.component.contact_frame_columns import CFrameColumns

from ctui.component.contact_details_frame import CDetailsFrame
from ctui.component.contact_list import ContactList
from ctui.enum.view import View


class UI:
    def __init__(self, core, config):
        self.core = core
        self.core.register_ui(self)
        self.name = 'frame'

        # TODO refactor
        self.current_contact = None
        self.current_contact_pos = None
        self.current_detail_pos = None
        self.core.filter_mode = False  # TODO

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
        self.watch_focus()  # TODO remove
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

    def focus_contact(self, contact):
        self.focus_list_view()
        self.list_view.set_focused_contact(contact)

    def focus_detail(self, detail):
        # TODO remove this or focus_detail_pos?
        self.focus_detail_view()  # TODO is this good? shouldn't it be separate?
        self.detail_view.focus_detail(detail)

    def focus_detail_pos(self, detail_pos):
        # TODO remove this or focus_detail?
        self.focus_detail_view()
        self.detail_view.focus_detail_pos(detail_pos)

    def refresh_contact_list(self, action=None, contact=None, detail=None,
                             filter_string=''):
        # TODO refactor

        if action is not Action.FILTERING and action is not Action.FILTERED:
            contact_list = self.core.get_all_contacts()
            self.core.contact_list = contact_list

        contact_list = self.core.get_filtered_contacts(filter_string)

        if action is Action.CONTACT_ADDED_OR_EDITED or \
                action is Action.CONTACT_DELETED or \
                action is Action.FILTERING or \
                action is Action.FILTERED or \
                action is Action.REFRESH:
            self.set_contact_list(contact_list)

        if contact is None:
            contact = self.list_view.get_focused_contact()

        self.core.update_contact_details(contact)

        if action is not Action.FILTERING:
            self.refresh_focus(action, contact, detail)

    def refresh_focus(self, action=None, contact=None, detail=None):
        # TODO refactor
        contact_pos = None
        detail_pos = None

        if action is Action.CONTACT_ADDED_OR_EDITED:
            contact_pos = self.list_view.get_contact_position(contact)
            detail_pos = 0
            self.frame.body.focus_position = 0
        elif action is Action.CONTACT_DELETED:
            contact_pos = min(self.current_contact_pos,
                              len(self.list_view.contents) - 1)
            detail_pos = 0
        elif action is Action.DETAIL_ADDED_OR_EDITED:
            detail_pos = self.detail_view.body.original_widget.get_detail_position(
                detail)
            self.frame.body.focus_position = 1
        elif action is Action.DETAIL_DELETED:
            if self.core.contact_handler.has_details(contact):
                # don't focus details column if contact has no details
                detail_pos = min(self.current_detail_pos,
                                 len(self.detail_view.body.original_widget.body) - 1)
                self.frame.body.focus_position = 1
            else:
                detail_pos = 0
        elif action is Action.FILTERING or action is Action.FILTERED:
            contact_pos = self.list_view.get_contact_position(
                self.current_contact)
            detail_pos = 0
        elif action is Action.REFRESH:
            contact_pos = self.list_view.get_contact_position(
                self.current_contact)
            detail_pos = 0
        else:  # defaults
            contact_pos = 0
            detail_pos = 0

        # update focused contact
        if contact_pos is not None:
            self.list_view.set_focus_position(contact_pos)

        # update focused detail
        self.detail_view.body.original_widget.set_focus_position(detail_pos)

        # update focus watchers (esp. for testing; usually keyboard already triggers this)
        self.watch_focus()

    def watch_focus(self):
        # TODO refactor
        self.current_contact = self.list_view.get_focused_contact()
        self.current_contact_pos = self.list_view.get_focus_position()

        # TODO schlägt fehl bei Navigation über keybindings
        self.current_detail_pos = self.detail_view.body.original_widget.get_focus_position()

        # TODO make configurable as debug mode?
        focus_str = "{} {}".format(str(self.current_contact_pos),
                                   str(self.current_detail_pos))
        self.console.show_meta(focus_str)

    def update_view(self,
                    update_contact_list=False,
                    update_contact_details=False,
                    focused_view=None,
                    focused_contact=None,
                    focused_detail=None):
        curr_contact_pos = self.list_view.get_focus_position()
        curr_detail_pos = self.detail_view.get_tab_body().get_focus_position()

        if update_contact_list:
            # TODO refactor
            self.core.contact_list = self.core.get_all_contacts()
            contact_list = self.core.get_filtered_contacts(
                self.core.get_filter_string())  # keep filter applied
            self.core.ui.set_contact_list(contact_list)

        if focused_view is View.LIST:
            self.focus_list_view()
        elif focused_view is View.DETAIL:
            self.focus_detail_view()

        list_count = self.list_view.get_count()
        if isinstance(focused_contact, int):
            contact_pos = focused_contact
        elif focused_contact is None:
            contact_pos = curr_contact_pos
        else:
            contact_pos = self.list_view.get_contact_position(focused_contact)

        if list_count > 0 and contact_pos is not None:  # contact_pos can be None if curr_detail_pos is None
            contact_pos = min(contact_pos, list_count - 1)
            self.list_view.set_focus_position(contact_pos)

        detail_count = self.detail_view.get_tab_body().get_count()
        if isinstance(focused_detail, int):
            detail_pos = focused_detail
        elif focused_detail is None:
            detail_pos = curr_detail_pos
        else:
            detail_pos = self.detail_view.get_tab_body().get_detail_position(
                focused_detail)

        if detail_count > 0 and detail_pos is not None:  # detail_pos can be None if curr_detail_pos is None
            detail_pos = min(detail_pos, detail_count - 1)
            self.detail_view.get_tab_body().set_focus_position(detail_pos)

        # do this after the contact focus is updated
        if update_contact_details:
            contact = self.list_view.get_focused_contact()
            self.core.update_contact_details(contact)
