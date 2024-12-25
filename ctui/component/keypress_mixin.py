class KeypressMixin:
    def handle_keypress(self, size, key):
        """
        Shared keypress logic for all urwid components.
        """

        # Call the parent's keypress explicitly
        if hasattr(super(type(self), self), 'keypress'):
            key = super(type(self), self).keypress(size, key)
        else:
            raise NotImplementedError(
                f"Base class for {type(self).__name__} must implement `keypress`."
            )

        if key is None:
            return None

        command_id, command_key, command_repeat = self.core.keybindings.keypress(
            key, self.name)

        if command_id in self.get_command_map():
            return KeypressMixin.execute_command(self, command_id,
                                                 command_repeat, size)

        self.core.keybindings.set(command_key, command_repeat)
        self.core.keybindings.set_bubbling(True)
        return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)
