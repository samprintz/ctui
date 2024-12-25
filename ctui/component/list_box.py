import urwid

from ctui.component.keypress_mixin import KeypressMixin, KeybindingCommand


class CListBox(urwid.ListBox, KeypressMixin):
    def __init__(self, listwalker, core, name):
        super(CListBox, self).__init__(listwalker)
        self.core = core
        self.name = name

    def keypress(self, size, key):
        return self.handle_keypress(size, key, CListBox)

    @KeybindingCommand("move_down")
    def move_down(self, command_repeat, size):
        n = 1 if command_repeat == 0 else command_repeat  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CListBox, self).keypress(size, 'down')
        self.core.keybindings.set_simulating(False)

    @KeybindingCommand("move_up")
    def move_up(self, command_repeat, size):
        n = 1 if command_repeat == 0 else command_repeat  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CListBox, self).keypress(size, 'up')
        self.core.keybindings.set_simulating(False)

    @KeybindingCommand("jump_to_first")
    def jump_to_first(self, command_repeat, size):
        self.core.keybindings.set_simulating(True)
        # 2x as workaround, otherwise list focus not updated
        super(CListBox, self).keypress(size, 'home')
        super(CListBox, self).keypress(size, 'home')
        self.core.keybindings.set_simulating(False)

    @KeybindingCommand("jump_to_last")
    def jump_to_last(self, command_repeat, size):
        self.core.keybindings.set_simulating(True)
        # 2x as workaround, otherwise list focus not updated
        super(CListBox, self).keypress(size, 'end')
        super(CListBox, self).keypress(size, 'end')
        self.core.keybindings.set_simulating(False)
