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
