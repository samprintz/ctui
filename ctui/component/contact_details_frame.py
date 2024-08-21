import urwid


class ContactListBox(urwid.ListBox):
    def __init__(self, items):
        body = urwid.SimpleFocusListWalker([urwid.Text(item) for item in items])
        super().__init__(body)


class ContactTabs(urwid.Columns):
    def __init__(self, tab_names, callback):
        self.buttons = [urwid.Button(name, on_press=callback, user_data=name)
                        for name in tab_names]
        super().__init__(self.buttons)


class ContactMainContainer(urwid.WidgetPlaceholder):
    def __init__(self, initial_widget):
        super().__init__(initial_widget)


class ContactTitle(urwid.Text):
    def __init__(self, title):
        super().__init__(title, align='center')


class ContactHeader(urwid.Pile):
    def __init__(self, title_widget, tabs_widget):
        super().__init__([title_widget, tabs_widget])


class CDetailsFrame(urwid.Frame):
    def __init__(self, core, config):
        self.core = core
        self.name = 'details_frame'

        general_list = ContactListBox(
            ["General item 1", "General item 2", "General item 3"])
        gifts_list = ContactListBox(
            ["Gift item 1", "Gift item 2", "Gift item 3"])
        notes_list = ContactListBox(
            ["Note item 1", "Note item 2", "Note item 3"])

        # Dictionary to hold the ListBox widgets for easy access
        tab_content = {
            'General': general_list,
            'Gifts': gifts_list,
            'Notes': notes_list,
        }

        # Function to switch tabs
        def on_tab_click(button, tab_name):
            body.original_widget = tab_content[tab_name]

        # Create tab buttons
        self.tabs = ContactTabs(['General', 'Gifts', 'Notes'], on_tab_click)

        # Create a title widget
        title = ContactTitle("Tab Example")

        # Create a Pile for the title and the tabs
        header = ContactHeader(title, self.tabs)

        # Main container that will display the content of the selected tab
        body = ContactMainContainer(general_list)

        super(CDetailsFrame, self).__init__(header=header, body=body)

    def set_contact(self, contact):
        title = ContactTitle(contact.name)
        self.header = ContactHeader(title, self.tabs)
