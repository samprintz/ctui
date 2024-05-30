class Keybindings:

    default_context = 'global'

    def __init__(self, config):
        self.commands = {}
        self.is_bubbling: bool = False  # true if lower widgets pass a keypress to a higher widget
        self.is_disabled: bool = False  # true if a keypress is simulated (a key is mapped to another
        self.current_context = None
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
                        print(f'Warning: Key sequence "{key_sequence}" is assigned multiple times')

                    self.commands[context][key_sequence] = command_id

    def set(self, keys, repeat):
        if not self.is_disabled:
            self.current_keys = keys
            self.current_repeat = repeat

    def reset(self):
        self.is_bubbling = False
        self.current_context = None
        self.current_keys = []
        self.current_repeat = 0

    def set_bubbling(self, value):
        if not self.is_disabled:
            self.is_bubbling = value

    def set_simulating(self, value):
        self.is_disabled = value

    def keypress(self, key, context):
        new_context = context != self.current_context

        if new_context:
            self.current_context = context

        if self.is_bubbling:
            self.is_bubbling = False
            return

        if key.isdigit():
            if self.current_repeat > 0:
                self.current_repeat = int(str(self.current_repeat) + key)
            else:
                self.current_repeat = int(key)
        else:
            self.current_keys.append(key)

    def eval(self):
        current_keys = self.current_keys
        current_repeat = self.current_repeat
        command_id = None
        key_sequence_exists = False

        current_key_sequence = ''.join(current_keys)
        contexts = [Keybindings.default_context, self.current_context]

        for context_iter in contexts:
            if context_iter in self.commands:
                for key_sequence in self.commands[context_iter].keys():
                    if key_sequence.startswith(current_key_sequence):
                        key_sequence_exists = True

        if key_sequence_exists:
            for context_iter in contexts:
                if context_iter in self.commands:
                    if current_key_sequence in self.commands[context_iter]:
                        command_id = self.commands[context_iter][
                            current_key_sequence]

        if not key_sequence_exists or command_id is not None:
            self.reset()

        return command_id, current_keys, current_repeat
