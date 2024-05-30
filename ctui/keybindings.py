class Keybindings:

    def __init__(self, config):
        self.commands = {}
        self.current_context = None
        self.current_keys = []  # used for multi-key-bindings
        self.load(config)
        self.default_context = 'global'

    def load(self, config):
        for config_section, config_entry in config.items():
            if 'keybindings' in config_section:
                context = config_section.replace('keybindings.', '')
                for command_id, key_sequence in config_entry.items():
                    if context not in self.commands:
                        self.commands[context] = {}

                    if key_sequence in self.commands[context]:
                        print(f'Warning: Key sequence "{key_sequence}" is used multiple times')

                    self.commands[context][key_sequence] = command_id

    def set(self, keys):
        self.current_keys = keys

    def keypress(self, key, context):
        new_context = context != self.current_context

        if new_context:
            self.current_context = context
            self.current_keys = []

        self.current_keys.append(key)

    def eval(self):
        current_keys = self.current_keys
        command_id = None
        key_sequence_exists = False

        current_key_sequence = ''.join(current_keys)
        contexts = [self.default_context, self.current_context]

        for context_iter in contexts:
            for key_sequence in self.commands[context_iter].keys():
                if key_sequence.startswith(current_key_sequence):
                    key_sequence_exists = True

        if key_sequence_exists:
            for context_iter in contexts:
                if current_key_sequence in self.commands[context_iter]:
                    command_id = self.commands[context_iter][
                        current_key_sequence]

        if not key_sequence_exists or command_id is not None:
            self.current_keys = []

        return command_id, current_keys
