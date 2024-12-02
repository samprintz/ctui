from datetime import datetime, date

import urwid

from ctui.commands import AddAttribute, AddNote, AddEncryptedNote


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
            case 'add_contact':
                command = 'add-contact '
                self.core.ui.console.show_console(command)
            case 'add_attribute':
                command = f'{AddAttribute.name} '
                self.core.ui.console.show_console(command)
            case 'add_note':
                note_id = datetime.strftime(date.today(), "%Y%m%d")
                command = f'{AddNote.name} {note_id}'
                self.core.ui.console.show_console(command)
            case 'add_encrypted_note':
                note_id = datetime.strftime(date.today(), "%Y%m%d")
                command = f'{AddEncryptedNote.name} {note_id}'
                self.core.ui.console.show_console(command)
            case _:
                self.core.keybindings.set_bubbling(False)
                if not self.core.keybindings.is_prefix(command_key):
                    self.core.keybindings.reset()
                return key
