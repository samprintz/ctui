class Keybindings:

    def __init__(self, config):
        self.commands = {}
        self.current_context = None
        self.current_keys = []  # used for multi-key-bindings
        self.load(config)

    def load(self, config):
        for config_section, config_entry in config.items():
            if 'keybindings' in config_section:
                context = config_section.replace('keybindings.', '')
                for command_id, key_sequence in config_entry.items():
                    if context not in self.commands:
                        self.commands[context] = {}

                    self.commands[context][command_id] = {
                        'key_sequence': key_sequence
                    }

    def register(self, commands, context):
        if context not in self.commands:
            self.commands[context] = {}

        for command in commands:
            if command['id'] in self.commands[context]:
                self.commands[context][command['id']]['function'] = \
                    command['function']

    def press(self, key, context):
        if context != self.current_context:
            self.current_context = context
            self.current_keys = []

        self.current_keys.append(key)
        key_sequence = ''.join(self.current_keys)
        self.call(key_sequence, context)

    def call(self, key_sequence, context):
        function = None
        key_sequence_exists = False

        if context in self.commands:
            for command_id, command in self.commands[context].items():
                if command['key_sequence'].startswith(key_sequence):
                    key_sequence_exists = True
                if command['key_sequence'] == key_sequence:
                    function = command['function']
                    self.current_keys = []

        if not key_sequence_exists:
            self.current_keys = []

        if function:
            function()
