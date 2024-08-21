import urwid

from ctui.cli import Action


class ContactFrame(urwid.Frame):
    def __init__(self, config, core):
        super(ContactFrame, self).__init__(None)
        self.config = config
        self.name = 'frame'
        self.core = core
        self.first_detail_pos = 2
        self.current_contact = None
        self.current_contact_pos = None
        self.current_detail = None
        self.current_detail_pos = None
        self.core.filter_mode = False

        self.body = ContactFrameColumns(self.core, self.config)
        self.footer = urwid.BoxAdapter(Console(self.core), height=1)

        self.set_contacts(core.contact_list)

    def get_contact_list_column(self):
        return self.body.contents[0][0].base_widget

    def get_contact_details_column(self):
        return self.body.contents[1][0].base_widget

    def get_console(self):
        return self.footer.original_widget

    def set_contacts(self, contacts):
        self.get_contact_list_column().set_contact_list(contacts)

        focused_contact = self.get_contact_list_column().get_focused_contact()
        focused_contact.get_details()  # augment existing contact with details (not before for performance)
        self.get_contact_details_column().set_contact_details(focused_contact)

        # self.watch_focus()

    def refresh_contact_list(self, action=None, contact=None, detail=None,
                             filter_string=''):
        if action is not Action.FILTERING and action is not Action.FILTERED:
            contact_list = self.core.get_all_contacts()
            self.core.contact_list = contact_list
        contact_list = self.core.filter_contacts(filter_string)
        if action is Action.CONTACT_ADDED_OR_EDITED or \
                action is Action.CONTACT_DELETED or \
                action is Action.FILTERING or \
                action is Action.FILTERED or \
                action is Action.REFRESH:
            self.get_contact_list_column().set_contact_list(contact_list)
        self.get_contact_details_column().set_contact_details(contact)
        if action is not Action.FILTERING:
            self.refresh_focus(action, contact, detail)

    def refresh_focus(self, action=None, contact=None, detail=None):
        contact_pos = None
        detail_pos = None

        if action is Action.CONTACT_ADDED_OR_EDITED:
            contact_pos = self.contact_list.get_contact_position(contact)
            detail_pos = 0
            self.body.set_focus_column(0)
        elif action is Action.CONTACT_DELETED:
            contact_pos = min(self.current_contact_pos,
                              len(self.contact_list.body) - 1)
            detail_pos = 0
        elif action is Action.DETAIL_ADDED_OR_EDITED:
            detail_pos = self.contact_details.get_detail_position(detail)
            self.body.set_focus_column(1)
        elif action is Action.DETAIL_DELETED:
            if contact.has_details():  # don't focus details column if contact has no details
                detail_pos = min(self.current_detail_pos,
                                 len(self.contact_details.body) - 1)
                self.body.set_focus_column(1)
            else:
                detail_pos = 0
        elif action is Action.FILTERING or action is Action.FILTERED:
            contact_pos = self.contact_list.get_contact_position(
                self.current_contact)
            detail_pos = 0
        elif action is Action.REFRESH:
            contact_pos = self.contact_list.get_contact_position(
                self.current_contact)
            detail_pos = 0
        else:  # defaults
            contact_pos = 0
            detail_pos = 0

        # update focused contact
        if contact_pos is not None:
            self.contact_list.set_focus_position(contact_pos)

        # update focused detail
        self.contact_details.set_focus_position(detail_pos)

        # update focus watchers (esp. for testing; usually keyboard already triggers this)
        self.watch_focus()

    def watch_focus(self):
        self.current_contact = self.contact_list.get_focused_contact()
        self.current_contact_pos = self.contact_list.get_focus_position()
        self.current_detail = self.contact_details.get_focused_detail()
        self.current_detail_pos = self.contact_details.get_focus_position()
        # focus_str = "{} {}".format(str(self.current_contact_pos), str(self.current_detail_pos))
        # self.console.show_meta(focus_str)

    def clear_footer(self):
        self.footer = urwid.BoxAdapter(Console(self.core), height=1)
        self.console = self.footer.original_widget
        self.set_focus('body')

    def details_focused(self):
        return self.body.get_focus_column() == 1

    def keypress(self, size, key):
        if key == 'esc':
            self.core.keybindings.reset()
            return super(ContactFrame, self).keypress(size, key)

        key = super(ContactFrame, self).keypress(size, key)
        if key is None:
            self.core.keybindings.reset()
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'reload':
                self.core.frame.watch_focus()
                self.core.frame.refresh_contact_list(Action.REFRESH, None, None,
                                                     self.core.filter_string)
            case 'add_contact':
                self.core.cli.add_contact()
            case 'add_attribute':
                focused_contact = self.core.frame.contact_list \
                    .get_focused_contact()
                self.core.cli.add_attribute(focused_contact)
            case 'add_note':
                focused_contact = self.core.frame.contact_list \
                    .get_focused_contact()
                self.core.cli.add_note(focused_contact)
            case 'add_encrypted_note':
                focused_contact = self.core.frame.contact_list. \
                    get_focused_contact()
                self.core.cli.add_encrypted_note(focused_contact)
            case _:
                self.core.keybindings.set_bubbling(False)
                if not self.core.keybindings.is_prefix(command_key):
                    self.core.keybindings.reset()
                return key


class ContactDetails(urwid.Pile):
    def __init__(self, contact, core):
        widget_list = [
            urwid.Text(contact.name, align='center'),
            urwid.Text("test", align='center')
            # ContactTabs(contact, core)
        ]

        super(ContactDetails, self).__init__(widget_list)
        self.core = core


class ContactTabs(urwid.Pile):
    def __init__(self, contact, core):
        tab_buttons = urwid.Columns([
            urwid.Button("General", on_press=self.on_tab_click,
                         user_data='General'),
            urwid.Button("Gifts", on_press=self.on_tab_click,
                         user_data='Gifts'),
            urwid.Button("Notes", on_press=self.on_tab_click,
                         user_data='Notes'),
        ])

        # general_tab = ContactDetails(contact, core)
        general_tab = urwid.Text("general...", align='center'),
        gift_tab = urwid.Text("gifts...", align='center'),
        note_tab = urwid.Text("notes...", align='center'),

        widget_list = [
            tab_buttons,
            # urwid.WidgetPlaceholder(general_tab)
            general_tab
        ]

        super(ContactTabs, self).__init__(widget_list)

        self.core = core
        self.tab_content = {
            'General': general_tab,
            'Gifts': gift_tab,
            'Notes': note_tab,
        }

    def on_tab_click(self, button, tab_name):
        self.original_widget = self.tab_content[tab_name]
