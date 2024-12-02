import urwid

from ctui.commands import Command


class Console(urwid.Filler):
    def __init__(self, core):
        super(Console, self).__init__(urwid.Text(''))
        self.core = core
        self.name = 'console'
        self.filter_mode = False

    def show_console(self, command=''):
        self.body = urwid.Edit(":", command)
        self.core.ui.frame.focus_position = 'footer'

    def show_message(self, message):
        self.body = urwid.Text(message)

    def show_input(self, request):
        self.body = urwid.Edit("{}?".format(request))
        self.core.ui.frame.focus_position = 'footer'

    def show_search(self):
        self.body = urwid.Edit("/")
        self.core.ui.frame.focus_position = 'footer'

    def show_filter(self, command):
        self.filter_mode = True
        self.show_console(command)

    def show_passphrase_input(self):
        self.body = urwid.Edit("Passphrase: ", mask="*")
        self.core.ui.frame.focus_position = 'footer'

    def show_meta(self, meta):
        self.body = urwid.AttrMap(urwid.Text(meta, 'right'), 'status_bar')

    def handle(self, args):
        command = args[0]
        for command_class in Command.__subclasses__():
            if command in command_class.names:
                command_instance = command_class(self.core)
                command_instance.execute(args[1:])
                break

    def clear(self):
        self.body = urwid.Text('')

    def keypress(self, size, key):
        if key == 'ctrl w':
            last_whitespace = self.original_widget.edit_text.rfind(' ')
            if last_whitespace != -1:
                text = (self.original_widget.edit_text[:last_whitespace]) + ' '
            else:
                text = ''
            self.original_widget.edit_text = text
            return
        if self.filter_mode is True:
            if key == 'esc':
                self.filter_mode = False
                self.clear()
                self.core.unfilter_contacts()
                return
            elif key == 'enter':
                self.filter_mode = False
                msg = 'f={}'.format(self.core.filter_string)
                self.show_message(msg)
                self.core.ui.frame.focus_position = 'body'
                return
            else:
                super(Console, self).keypress(size, key)
                args = self.original_widget.edit_text.split()
                filter_string = " ".join(args[0:])
                return self.core.update_contact_list(filter_string)
        else:
            if key == 'esc':
                self.clear()
                self.core.ui.frame.focus_position = 'body'
            elif key == 'enter':
                args = self.original_widget.edit_text.split()
                self.core.handle(args)
                self.core.ui.frame.focus_position = 'body'
            else:
                return super(Console, self).keypress(size, key)
