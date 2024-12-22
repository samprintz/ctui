import urwid


class CFrame(urwid.Frame):
    def __init__(self, body, footer, core, config):
        super(CFrame, self).__init__(body=body, footer=footer)
        self.core = core
        self.name = 'frame'

    def keypress(self, size, key):
        if key == 'esc':
            self.core.keybindings.reset()
            return super(CFrame, self).keypress(size, key)

        key = super(CFrame, self).keypress(size, key)
        if key is None:
            self.core.keybindings.reset()
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set_bubbling(False)
            if not self.core.keybindings.is_prefix(command_key):
                self.core.keybindings.reset()
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def quit_app(command_repeat, size):
            raise urwid.ExitMainLoop()

        def reload(command_repeat, size):
            self.core.update_contact_list()

        def open_console(command_repeat, size):
            self.core.ui.console.show_console()

        def add_contact(command_repeat, size):
            command = 'add-contact '
            self.core.ui.console.show_console(command)

        def add_detail(command_repeat, size):
            self.core.ui.detail_view.get_tab_body().execute_command(
                "add_detail", command_repeat, size)

        def next_tab(command_repeat, size):
            self.core.ui.next_tab()

        def previous_tab(command_repeat, size):
            self.core.ui.previous_tab()

        return {
            'quit': quit_app,
            'reload': reload,
            'open_console': open_console,
            'add_contact': add_contact,
            'add_detail': add_detail,
            'next_tab': next_tab,
            'previous_tab': previous_tab,
        }
