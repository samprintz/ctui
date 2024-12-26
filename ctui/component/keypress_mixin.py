class KeypressMixin:

    def get_command_map(self):
        """
        Collect all methods of urwid components with @KeybindingCommand decorator.
        """
        command_map = {}
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
                if callable(attr) and hasattr(attr, "_keybinding_command"):
                    keybinding_command = getattr(attr, "_keybinding_command")
                    command_map[keybinding_command] = attr
            except (IndexError, AttributeError):
                # Ignore IndexError for missing focus_position of empty Listbox
                # Ignore AttributeError for missing get_pref_col of SelectableIcon
                pass
        return command_map

    def handle_keypress(self, size, key, current_type=None,
                        is_final_component=False):
        """
        Shared keypress logic for all urwid components.

        Args:
            size (tuple): Size of the widget
            key (str): Key that was pressed
            current_type (type, optional): The class to use as the base for the
            `super` call. Required for keybindings of base class components
            (like CListBox).
            is_final_component (boolean, optional): Set True if this is final
            (last, most outer) component that could handle a keybinding.
        """

        # Call the parent's keypress explicitly
        base_class = current_type if current_type else type(self)
        if hasattr(super(base_class, self), 'keypress'):
            key = super(base_class, self).keypress(size, key)
        else:
            raise NotImplementedError(
                f"Base class for {type(self).__name__} must implement `keypress`."
            )

        if key is None:
            if is_final_component:
                self.core.keybindings.reset()

            return None

        command_id, command_key, command_repeat = self.core.keybindings.keypress(
            key, self.name)

        # TODO reference self instead of KeypressMixin
        if command_id in KeypressMixin.get_command_map(self):
            # TODO reference self instead of KeypressMixin
            return KeypressMixin.execute_command(self, command_id,
                                                 command_repeat, size)

        if is_final_component:
            self.core.keybindings.set_bubbling(False)
            if not self.core.keybindings.is_prefix(command_key):
                self.core.keybindings.reset()
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)

        return key

    def execute_command(self, command_id, command_repeat, size):
        # TODO reference self instead of KeypressMixin
        command = KeypressMixin.get_command_map(self)[command_id]
        return command(command_repeat, size)


def KeybindingCommand(keybinding_command):
    """
    Decorator to assign keybindings to urwid component functions by specifying a
    command name.
    """

    def decorator(func):
        if not hasattr(func, "_keybinding_command"):
            func._keybinding_command = keybinding_command
        return func

    return decorator
