import urwid

from ctui.component.keypress_mixin import KeypressMixin, KeybindingCommand


class CFrame(urwid.Frame, KeypressMixin):
    def __init__(self, body, footer, core, config):
        super(CFrame, self).__init__(body=body, footer=footer)
        self.core = core
        self.name = 'frame'

    def keypress(self, size, key):
        return self.handle_keypress(size, key, None, True)

    @KeybindingCommand("quit")
    def quit_app(self, command_repeat, size):
        raise urwid.ExitMainLoop()

    @KeybindingCommand("reload")
    def reload(self, command_repeat, size):
        focused_contact = self.core.ui.get_focused_contact()
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(focused_contact.get_id())

    @KeybindingCommand("open_console")
    def open_console(self, command_repeat, size):
        self.core.ui.console.show_console()

    @KeybindingCommand("add_contact")
    def add_contact(self, command_repeat, size):
        command = 'add-contact '
        self.core.ui.console.show_console(command)

    @KeybindingCommand("add_detail")
    def add_detail(self, command_repeat, size):
        self.core.ui.detail_view.get_tab_body().execute_command(
            "add_detail", command_repeat, size)

    @KeybindingCommand("next_tab")
    def next_tab(self, command_repeat, size):
        self.core.ui.next_tab()

    @KeybindingCommand("previous_tab")
    def previous_tab(self, command_repeat, size):
        self.core.ui.previous_tab()
