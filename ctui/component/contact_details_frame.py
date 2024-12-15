import urwid

from ctui.component.contact_details import GeneralDetails, GiftDetails, \
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
        self.tab_names = ['General', 'Gifts', 'Notes']
        self.tab_content = {}
        self.current_tab = 0

    def on_tab_click(self, button, tab_name):
        self.body.original_widget = self.tab_content[tab_name]
        self.header.update_selected_tab_button(self.current_tab)

    def set_contact(self, contact_id: str) -> None:
        self.tab_content = {
            'General': GeneralDetails(contact_id, self.core),
            'Gifts': GiftDetails(contact_id, self.core),
            'Notes': NoteDetails(contact_id, self.core)
        }

        self.header = CDetailTabNavigation(self.tab_names, self.on_tab_click)
        self.body = CDetailTabBody(self.tab_content['General'])

        # keep the latest selected tab selected after detail updates
        self.set_tab(self.current_tab)

    def get_tab_body(self):
        return self.body.original_widget

    def get_tab(self):
        return self.current_tab

    def set_tab(self, tab):
        self.current_tab = tab
        tab_name = self.tab_names[self.current_tab]
        self.on_tab_click(None, tab_name)

    def next_tab(self):
        tab = (self.current_tab + 1) % len(self.tab_names)
        self.set_tab(tab)

    def previous_tab(self):
        tab = (self.current_tab - 1) % len(self.tab_names)
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
