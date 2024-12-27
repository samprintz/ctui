from typing import Tuple, Optional


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

    def handle_keypress(self,
                        size: Tuple[int, int],
                        key: str,
                        base_class_type: Optional[type] = None,
                        is_final_component: bool = False
                        ) -> Optional[str]:
        """
        Shared keypress logic for all urwid components.

        Args:
            size (tuple): Size of the widget
            key (str): Key that was pressed
            base_class_type (type, optional): Required for keybindings of base
            class components (like CListBox).
            is_final_component (boolean, optional): Set True if this is final
            (last, most outer) component that could handle a keybinding.
        """
        key = self._call_parent_keypress(size, key, base_class_type)
        if key is None:
            if is_final_component:
                self.core.keybindings.reset()
            return None

        command_map = self.get_command_map()
        command_id, command_key, command_repeat = self.core.keybindings.keypress(
            key, self.name)

        if command_id in command_map:
            return command_map[command_id](command_repeat, size)

        self._handle_keybinding_state(command_key, command_repeat,
                                      is_final_component)
        return key

    def _call_parent_keypress(self,
                              size: Tuple[int, int],
                              key: str,
                              base_class_type: Optional[type]
                              ) -> Optional[str]:
        """
        Calls the parent's keypress explicitly.
        """
        base_class = base_class_type if base_class_type else type(self)
        if hasattr(super(base_class, self), 'keypress'):
            return super(base_class, self).keypress(size, key)
        raise NotImplementedError(
            f"Base class for {type(self).__name__} must implement `keypress`."
        )

    def _handle_keybinding_state(self,
                                 command_key: str,
                                 command_repeat: int,
                                 is_final_component: bool
                                 ) -> None:
        """
        Manages the keybinding state based on the context.
        """
        if is_final_component:
            self.core.keybindings.set_bubbling(False)
            if not self.core.keybindings.is_prefix(command_key):
                self.core.keybindings.reset()
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)


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
