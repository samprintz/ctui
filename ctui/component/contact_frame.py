import urwid

from ctui.cli import Action


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
                self.core.ui.watch_focus()
                self.core.ui.refresh_contact_list(Action.REFRESH, None, None,
                                                  self.core.filter_string)
            case 'add_contact':
                self.core.cli.add_contact()
            case 'add_attribute':
                focused_contact = self.core.ui.list_view \
                    .get_focused_contact()
                self.core.cli.add_attribute(focused_contact)
            case 'add_note':
                focused_contact = self.core.ui.list_view \
                    .get_focused_contact()
                self.core.cli.add_note(focused_contact)
            case 'add_encrypted_note':
                focused_contact = self.core.ui.list_view \
                    .get_focused_contact()
                self.core.cli.add_encrypted_note(focused_contact)
            case _:
                self.core.keybindings.set_bubbling(False)
                if not self.core.keybindings.is_prefix(command_key):
                    self.core.keybindings.reset()
                return key
