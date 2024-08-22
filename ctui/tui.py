import urwid


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
