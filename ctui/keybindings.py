from typing import Tuple, Optional


class Keybindings:
    default_context = 'global'

    def __init__(self, config):
        self.commands = {}
        self.is_bubbling: bool = False  # true if lower widgets pass a keypress to a higher widget
        self.is_disabled: bool = False  # true if a keypress is simulated (a key is mapped to another
        self.current_keys: list = []  # used for multi-key-bindings
        self.current_repeat: int = 0  # some commands can be executed multiple times
        self.load(config)

    def load(self, config):
        for config_section, config_entry in config.items():
            if 'keybindings' in config_section:
                context = config_section.replace('keybindings.', '')
                for command_id, key_sequence in config_entry.items():
                    if context not in self.commands:
                        self.commands[context] = {}

                    if key_sequence in self.commands[context]:
                        print(
                            f'Warning: Key sequence "{key_sequence}" is assigned multiple times')

                    self.commands[context][key_sequence] = command_id

    def set(self, keys, repeat):
        if not self.is_disabled:
            self.current_keys = keys
            self.current_repeat = repeat

    def reset(self):
        self.is_bubbling = False
        self.current_keys = []
        self.current_repeat = 0

    def set_bubbling(self, value):
        if not self.is_disabled:
            self.is_bubbling = value

    def set_simulating(self, value):
        self.is_disabled = value

    def keypress(self, key, context):
        command_id = None

        if not self.is_bubbling and not self.is_disabled:
            if key.isdigit():
                if self.current_repeat > 0:
                    self.current_repeat = int(str(self.current_repeat) + key)
                else:
                    self.current_repeat = int(key)
            else:
                self.current_keys.append(key)

        key_sequence = ''.join(self.current_keys)
        contexts = [Keybindings.default_context, context]
        current_keys = self.current_keys
        current_repeat = self.current_repeat

        if not self.is_disabled:
            command_id = self.get_command_id(key_sequence, contexts)

        if command_id:
            self.reset()

        return command_id, current_keys, current_repeat

    def after_keypress(self, key, current_repeat, is_final_component):
        if is_final_component:
            self.set_bubbling(False)
            if not self.is_prefix(key):
                self.reset()
        else:
            self.set(key, current_repeat)
            self.set_bubbling(True)

    def is_prefix(self, keys):
        key_sequence = ''.join(keys)
        for context in self.commands.keys():
            for key_sequence_iter in self.commands[context].keys():
                if (key_sequence_iter.startswith(key_sequence)
                        and not key_sequence_iter == key_sequence):
                    return True

    def get_command_id(self, key_sequence, contexts):
        for context_iter in contexts:
            if context_iter in self.commands:
                if key_sequence in self.commands[context_iter]:
                    return self.commands[context_iter][key_sequence]


class KeybindingMixin:

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
        self.core.keybindings.after_keypress(command_key, command_repeat,
                                             is_final_component)

        if command_id in command_map:
            return command_map[command_id](command_repeat, size)

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
