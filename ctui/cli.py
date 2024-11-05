from enum import Enum

from ctui.commands import Command


class CLI:
    """
    Vim-like console that serves as main user interface for data-manipulation (esp. create, update, delete).
    """

    def __init__(self, core):
        self.core = core
        self.contact = None
        self.detail = None
        self.filter_string = ''
        self.mode = None
        self.note = None

    def handle(self, args):
        if self.mode is Mode.SEARCH:
            name = " ".join(args[0:])
            msg = self.core.search_contact(name)
            self.mode = None
            self.action = None
            self.core.ui.frame.focus_position = 'body'
            self.core.ui.console.show_message(msg)

        elif self.mode is Mode.FILTER:
            if args is not False:
                filter_string = " ".join(args[1:])
                self.core.filter_string = filter_string
                self.filter_string = filter_string
                self.action = Action.FILTERING
                self.core.ui.refresh_contact_list(self.action, self.contact,
                                                  self.detail,
                                                  self.filter_string)
            else:  # enter was pressed
                self.action = Action.FILTERED
                self.core.ui.refresh_contact_list(self.action, self.contact,
                                                  self.detail,
                                                  self.filter_string)
                self.core.ui.frame.focus_position = 'body'
                msg = 'f={}'.format(self.core.filter_string)
                self.core.ui.console.show_message(msg)
                self.mode = None

        else:
            command = args[0]

            for command_class in Command.__subclasses__():
                if command in command_class.names:
                    command_instance = command_class(self.core)

                    # TODO pass a status snapshop object with
                    # focused_contact, focused_detail, focused_contact_pos, focused_detail_pos?
                    # TODO pass the args already joined (as id or name)? if not everywhere, then dependent on a class attribute?
                    # also validate it here?
                    command_instance.execute(args[1:])
                    # TODO execute view update commands (focus_detail() etc.) here depending on class attributes?

                    break

            self.core.ui.frame.focus_position = 'body'

    def search_contact(self):
        self.mode = Mode.SEARCH
        self.core.ui.console.show_search()

    def filter_contacts(self):
        self.mode = Mode.FILTER
        if self.core.filter_mode is False:
            self.core.filter_string = ''
        self.core.filter_mode = True
        command = 'filter {}'.format(self.core.filter_string)
        self.core.ui.console.show_filter(command)

    def unfilter_contacts(self):
        self.mode = None
        self.action = Action.FILTERED
        self.filter_string = ''
        self.core.filter_mode = False
        self.core.filter_string = ''
        self.core.ui.refresh_contact_list(self.action, self.contact,
                                          self.detail, self.filter_string)
        self.core.ui.console.clear()
        self.core.ui.frame.focus_position = 'body'


class Mode(Enum):
    SEARCH = 'search'
    FILTER = 'filter'
    CONSOLE = 'console'
    INPUT = 'input'


class Action(Enum):
    REFRESH = 'refresh'
    CONTACT_ADDED_OR_EDITED = 'contact_added_or_edited'
    CONTACT_DELETED = 'contact_deleted'
    DETAIL_ADDED_OR_EDITED = 'detail_added_or_edited'
    DETAIL_DELETED = 'detail_deleted'
    FILTERING = 'filtering'  # when the console is still open
    FILTERED = 'filtered'  # when filter string is entered and the console closed
