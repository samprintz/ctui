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

        match command_id:
            case 'quit':
                raise urwid.ExitMainLoop()
            case 'reload':
                self.core.update_contact_list()
            case 'open_console':
                self.core.ui.console.show_console()
            case 'add_contact':
                command = 'add-contact '
                self.core.ui.console.show_console(command)
            case 'add_detail':
                self.core.ui.detail_view.get_tab_body().execute_command(
                    command_id, command_key, command_repeat)
            case 'next_tab':
                self.core.ui.next_tab()
            case 'previous_tab':
                self.core.ui.previous_tab()
            case _:
                self.core.keybindings.set_bubbling(False)
                if not self.core.keybindings.is_prefix(command_key):
                    self.core.keybindings.reset()
                return key
