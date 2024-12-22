import urwid

from ctui.component.contact_details import AttributeDetails, GiftDetails, \
    NoteDetails


class CDetailTabNavigation(urwid.Columns):
    def __init__(self, tab_names, callback):
        self.buttons = [
            CTabButton(name, on_press=callback, user_data=name)
            for name in tab_names
        ]

        self.update_selected_tab_button(0)

        super().__init__(self.buttons)

    def update_selected_tab_button(self, tab_pos):
        for button in self.buttons:
            button.set_selected(False)
        self.buttons[tab_pos].set_selected(True)


class CTabButton(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")

    def __init__(self, label, on_press=None, user_data=None):
        super().__init__(label, on_press, user_data)
        self._w = urwid.AttrMap(self._w, None, focus_map='selected')

    def set_selected(self, selected):
        if selected:
            self._w.set_attr_map({None: 'selected'})
        else:
            self._w.set_attr_map({})


class CDetailTabBody(urwid.WidgetPlaceholder):
    def __init__(self, initial_widget):
        super().__init__(initial_widget)


class CDetailsFrame(urwid.Frame):
    def __init__(self, core, config):
        self.core = core
        self.name = 'details_frame'
        super(CDetailsFrame, self).__init__(None)
        self.tabs = []

        self.current_tab = 0

    def on_tab_click(self, button, tab_name):
        # TODO merge with set_tab?
        tab_pos = self.get_tab_pos_by_name(tab_name)
        self.body.original_widget = self.tabs[tab_pos]
        self.header.update_selected_tab_button(self.current_tab)

    def set_contact(self, contact_id: str) -> None:
        self.tabs = [
            NoteDetails(contact_id, self.core),
            GiftDetails(contact_id, self.core),
            AttributeDetails(contact_id, self.core),
        ]

        self.header = CDetailTabNavigation(self.get_tab_names(),
                                           self.on_tab_click)
        self.body = CDetailTabBody(self.tabs[0])

        # keep the latest selected tab selected after detail updates
        self.set_tab(self.current_tab)

    def get_tab_body(self):
        # TODO rename to get_current_tab()? and get_current_tab() to get_current_tab_id()?
        return self.body.original_widget

    def get_tab_names(self):
        return [tab.tab_name for tab in self.tabs]

    def get_tab_pos_by_id(self, tab_id: str) -> int:
        for idx, tab in enumerate(self.tabs):
            if tab.tab_id == tab_id:
                return idx
        return -1

    def get_tab_id_by_pos(self, tab_pos: int) -> str:
        if 0 <= tab_pos < len(self.tabs):
            return self.tabs[tab_pos].tab_id
        return ""

    def get_tab_pos_by_name(self, tab_name: str) -> int:
        for idx, tab in enumerate(self.tabs):
            if tab.tab_name == tab_name:
                return idx
        return -1

    def get_tab_name_by_pos(self, tab_pos: int) -> str:
        if 0 <= tab_pos < len(self.tabs):
            return self.tabs[tab_pos].tab_name
        return ""

    def get_tab(self) -> int:
        return self.current_tab

    def set_tab(self, tab: int) -> None:
        # TODO merge with on_tab_click?
        self.current_tab = tab
        tab_name = self.get_tab_name_by_pos(self.current_tab)
        self.on_tab_click(None, tab_name)

    def next_tab(self):
        tab = (self.current_tab + 1) % len(self.tabs)
        self.set_tab(tab)

    def previous_tab(self):
        tab = (self.current_tab - 1) % len(self.tabs)
        self.set_tab(tab)

    def get_current_tab_id(self) -> str:
        tab = self.get_tab()
        return self.get_tab_id_by_pos(tab)

    def set_current_tab_id(self, tab_id: str) -> None:
        tab = self.get_tab_pos_by_id(tab_id)
        self.set_tab(tab)

    def get_focused_detail(self):
        return self.get_tab_body().get_focused_detail()

    def set_focused_detail(self, detail):
        detail_pos = self.get_tab_body().get_detail_position(detail)
        self.set_focused_detail_pos(detail_pos)

    def get_focused_detail_pos(self):
        return self.get_tab_body().get_focus_position()

    def set_focused_detail_pos(self, detail_pos):
        self.get_tab_body().set_focus_position(detail_pos)

    def get_count(self) -> int:
        return self.get_tab_body().get_count()

    def keypress(self, size, key):
        key = super(CDetailsFrame, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_left':
                self.core.keybindings.set_simulating(True)
                key = super(CDetailsFrame, self).keypress(size, 'left')
                self.core.keybindings.set_simulating(False)
                return key
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
