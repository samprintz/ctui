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

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        # explicitly call this method of this class, otherwise the method of the
        # inheritor class (ContactList/DetailList) would be called
        if command_id in CListBox.get_command_map(self):
            return CListBox.execute_command(self, command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = CListBox.get_command_map(self)[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def move_down(command_repeat, size):
            n = 1 if command_repeat == 0 else command_repeat  # at least once
            self.core.keybindings.set_simulating(True)
            for i in range(0, n):
                super(CListBox, self).keypress(size, 'down')
            self.core.keybindings.set_simulating(False)

        def move_up(command_repeat, size):
            n = 1 if command_repeat == 0 else command_repeat  # at least once
            self.core.keybindings.set_simulating(True)
            for i in range(0, n):
                super(CListBox, self).keypress(size, 'up')
            self.core.keybindings.set_simulating(False)

        def jump_to_first(command_repeat, size):
            self.core.keybindings.set_simulating(True)
            # 2x as workaround, otherwise list focus not updated
            super(CListBox, self).keypress(size, 'home')
            super(CListBox, self).keypress(size, 'home')
            self.core.keybindings.set_simulating(False)

        def jump_to_last(command_repeat, size):
            self.core.keybindings.set_simulating(True)
            # 2x as workaround, otherwise list focus not updated
            super(CListBox, self).keypress(size, 'end')
            super(CListBox, self).keypress(size, 'end')
            self.core.keybindings.set_simulating(False)

        return {
            'move_down': move_down,
            'move_up': move_up,
            'jump_to_first': jump_to_first,
            'jump_to_last': jump_to_last,
        }
