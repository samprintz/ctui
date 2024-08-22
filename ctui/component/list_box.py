import urwid


class CListBox(urwid.ListBox):
    def __init__(self, listwalker, core, name):
        super(CListBox, self).__init__(listwalker)
        self.core = core
        self.name = name

    def keypress(self, size, key):
        key = super(CListBox, self).keypress(size, key)
        if key is None:
            return

        self.core.ui.watch_focus()

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_down':
                self.jump_down(size, command_repeat)
            case 'move_up':
                self.jump_up(size, command_repeat)
            case 'jump_to_first':
                self.core.keybindings.set_simulating(True)
                # 2x as workaround, otherwise list focus not updated
                super(CListBox, self).keypress(size, 'home')
                super(CListBox, self).keypress(size, 'home')
                self.core.keybindings.set_simulating(False)
            case 'jump_to_last':
                self.core.keybindings.set_simulating(True)
                # 2x as workaround, otherwise list focus not updated
                super(CListBox, self).keypress(size, 'end')
                super(CListBox, self).keypress(size, 'end')
                self.core.keybindings.set_simulating(False)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key

    def jump_down(self, size, n):
        n = 1 if n == 0 else n  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CListBox, self).keypress(size, 'down')
        self.core.keybindings.set_simulating(False)

    def jump_up(self, size, n):
        n = 1 if n == 0 else n  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CListBox, self).keypress(size, 'up')
        self.core.keybindings.set_simulating(False)
