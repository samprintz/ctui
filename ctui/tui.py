from datetime import datetime
import pyperclip
import urwid

from ctui.objects import Name, Attribute, Gift, Note, GoogleContact
from ctui.cli import Action


class ContactLoop(urwid.MainLoop):
    def __init__(self, frame, config):
        palette = [('selected', '', 'light gray')]
        loop = urwid.MainLoop(frame, palette, unhandled_input=self.show_or_exit)
        loop.run()

    def show_or_exit(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()


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


class ContactFrameColumns(urwid.Columns):
    def __init__(self, core, config):
        self.core = core
        self.focus_map = {'options': 'focus options'}
        self.nav_width = int(config['display']['nav_width'])

        widget_list = [
            (urwid.AttrMap(ContactList(contact_list, self.core),
                                'options', self.focus_map),
                  self.options('given', self.nav_width)),
            (ContactDetails(contact, self.core), self.options('weight', 1, True))
        ]

        super(ContactFrameColumns, self).__init__([], dividechars=1)

    def set_contact_list(self, contact_list):
        self.contents[0] = (urwid.AttrMap(ContactList(contact_list, self.core),
                                'options', self.focus_map),
                  self.options('given', self.nav_width))

    def set_contact_details(self, contact):
        self.contents[1] = (ContactDetails(contact, self.core),
                  self.options('weight', 1, True))


class CustListBox(urwid.ListBox):
    def __init__(self, listwalker, core, name):
        super(CustListBox, self).__init__(listwalker)
        self.core = core
        self.name = name

    def keypress(self, size, key):
        key = super(CustListBox, self).keypress(size, key)
        if key is None:
            return

        self.core.frame.watch_focus()

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_down':
                self.jump_down(size, command_repeat)
            case 'move_up':
                self.jump_up(size, command_repeat)
            case 'jump_to_first':
                self.core.keybindings.set_simulating(True)
                # 2x as workaround, otherwise list focus not updated
                super(CustListBox, self).keypress(size, 'home')
                super(CustListBox, self).keypress(size, 'home')
                self.core.keybindings.set_simulating(False)
            case 'jump_to_last':
                self.core.keybindings.set_simulating(True)
                # 2x as workaround, otherwise list focus not updated
                super(CustListBox, self).keypress(size, 'end')
                super(CustListBox, self).keypress(size, 'end')
                self.core.keybindings.set_simulating(False)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key

    def jump_down(self, size, n):
        n = 1 if n == 0 else n  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CustListBox, self).keypress(size, 'down')
        self.core.keybindings.set_simulating(False)

    def jump_up(self, size, n):
        n = 1 if n == 0 else n  # at least once
        self.core.keybindings.set_simulating(True)
        for i in range(0, n):
            super(CustListBox, self).keypress(size, 'up')
        self.core.keybindings.set_simulating(False)


class ContactList(CustListBox):
    def __init__(self, contact_list, core):
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactList, self).__init__(listwalker, core, 'contact_list')
        self.core = core
        self.set(contact_list)

    def set(self, contact_list):
        a = []
        pos = 0
        for c in contact_list:
            entry = ContactEntry(c, pos, self.core)
            urwid.connect_signal(entry, 'click',
                                 self.core.frame.set_contact_details)  # TODO in ListEntry
            a.append(entry)
            pos = pos + 1
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, 'modified',
                             self.core.frame.set_contact_details)

    def get_focused_contact(self):
        return self.focus.contact

    def set_focused_contact(self, contact):
        pos = self.get_contact_position(contact)
        self.set_focus(pos)

    def get_focus_position(self):
        return self.focus_position

    def set_focus_position(self, pos):
        self.focus_position = pos

    def get_contact_position(self, contact):
        pos = 0
        for entry in self.body:
            if entry.label == contact.name:
                return pos
            pos = pos + 1
        return None

    def get_contact_position_startswith(self, name):
        pos = 0
        for entry in self.body:
            if entry.label.lower().startswith(name.lower()):
                return pos
            pos = pos + 1
        return None

    def get_contact_position_contains(self, name):
        pos = 0
        for entry in self.body:
            if name.lower() in entry.label.lower():
                return pos
            pos = pos + 1
        return None

    def jump_to_contact(self, name):
        pos = self.get_contact_position_startswith(name)
        if pos is None:
            pos = self.get_contact_position_contains(name)
        if pos is not None:
            self.set_focus(pos)
            return True
        return False

    def keypress(self, size, key):
        key = super(ContactList, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_right':
                self.core.keybindings.set_simulating(True)
                key = super(ContactList, self).keypress(size, 'right')
                self.core.keybindings.set_simulating(False)
                return key
            case 'search_contact':
                self.core.cli.search_contact()
            case 'set_contact_filter':
                self.core.cli.filter_contacts()
            case 'clear_contact_filter':
                self.core.cli.unfilter_contacts()
            case 'add_google_contact':
                self.core.cli.add_google_contact()
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class ContactDetails(urwid.Pile):
    def __init__(self, contact, core):
        widget_list = [
            urwid.Text(contact.name, align='center'),
            urwid.Text("test", align='center')
            #ContactTabs(contact, core)
        ]

        super(ContactDetails, self).__init__(widget_list)
        self.core = core


class ContactTabs(urwid.Pile):
    def __init__(self, contact, core):
        tab_buttons = urwid.Columns([
            urwid.Button("General", on_press=self.on_tab_click, user_data='General'),
            urwid.Button("Gifts", on_press=self.on_tab_click, user_data='Gifts'),
            urwid.Button("Notes", on_press=self.on_tab_click, user_data='Notes'),
        ])

        # general_tab = ContactDetails(contact, core)
        general_tab = urwid.Text("general...", align='center'),
        gift_tab = urwid.Text("gifts...", align='center'),
        note_tab = urwid.Text("notes...", align='center'),

        widget_list = [
            tab_buttons,
            #urwid.WidgetPlaceholder(general_tab)
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


class ContactDetailsOld(CustListBox):
    def __init__(self, contact, core):
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactDetailsOld, self).__init__(listwalker, core, 'contact_details')
        self.core = core
        self.set(contact)

    def set(self, contact):
        name = DetailEntry(contact, Name(contact.name), contact.name, 0,
                           self.core)
        entries = [name, urwid.Divider()]
        pos = len(entries)

        if contact.attributes is not None:
            for a in contact.attributes:
                entries.append(
                    AttributeEntry(contact, Attribute(a[0], a[1]), pos,
                                   self.core))
                pos = pos + 1

        if type(contact) is GoogleContact and contact.google_attributes is not None:
            for a in contact.google_attributes:
                entries.append(GoogleAttributeEntry(contact, a, pos, self.core))
                pos = pos + 1

        if contact.gifts is not None:
            if len(entries) > 2:
                entries.append(urwid.Divider())
                pos = pos + 1
            entries.append(urwid.Text(u"GESCHENKE"))
            pos = pos + 1
            for a in contact.gifts:
                entries.append(GiftEntry(contact, Gift(a), pos, self.core))
                pos = pos + 1

        if type(contact) is GoogleContact and len(contact.google_notes) > 0:
            if len(entries) > 2:
                entries.append(urwid.Divider())
                pos = pos + 1
            entries.append(urwid.Text(u"NOTIZEN GOOGLE"))
            pos = pos + 1
            for note in contact.google_notes:
                entries.append(GoogleNoteEntry(contact, note, pos, self.core))
                pos = pos + 1

        if contact.notes is not None:
            if len(entries) > 2:
                entries.append(urwid.Divider())
                pos = pos + 1
            entries.append(urwid.Text(u"NOTIZEN"))
            pos = pos + 1
            for note in contact.notes:
                if type(note) is Note:  # plain note
                    entries.append(NoteEntry(contact, note, pos, self.core))
                else:  # encrypted note
                    # check if made visible
                    if contact.has_visible_note(note):
                        visible_note = contact.get_visible_note(note)
                        entries.append(
                            EncryptedNoteEntry(contact, visible_note, pos,
                                               self.core, visible=True))
                    else:
                        entries.append(
                            EncryptedNoteEntry(contact, note, pos, self.core))
                pos = pos + 1

        self.body = urwid.SimpleFocusListWalker(entries)
        urwid.connect_signal(self.body, 'modified', self.show_meta)

    def show_meta(self):
        if self.core.frame.details_focused() is True:
            if type(self.focus) is NoteEntry or type(
                    self.focus) is EncryptedNoteEntry:
                date = datetime.strftime(self.focus.note.date, '%d-%m-%Y')
                self.core.frame.console.show_meta(date)
            elif isinstance(self.focus, DetailEntry):
                self.core.frame.console.show_meta("")
                # self.core.frame.console.show_meta(str(self.focus.pos))
        else:
            self.core.frame.clear_footer()

    def number_of_details(self):
        return len(self.body) - 2

    def get_focused_detail(self):
        #        if not hasattr(self.focus, 'detail'):
        #            return None
        return self.focus.detail

    def get_focus_position(self):
        return self.focus_position

    def set_focus_position(self, pos):
        try:  # fix for frequent problem: # TODO undo this after improving get_detail_position()
            # "'<' not supported between instances of 'NoneType' and 'int'"
            self.focus_position = pos
        except TypeError:
            pass

    def get_detail_position(self, detail):
        pos = 0
        for entry in self.body:
            if isinstance(entry, DetailEntry):
                # TODO Workaround for gifts (as they are not recognized as gifts when creating them with add-attribute instead of add-gift
                if isinstance(detail,
                              Attribute) and detail.key == "giftIdea" and isinstance(
                    entry.detail, Gift):
                    if detail.value == entry.detail.name:
                        return pos
                else:
                    if type(entry.detail) == type(detail):
                        if entry.detail == detail:
                            return pos
            pos = pos + 1
        return None

    def keypress(self, size, key):
        key = super(ContactDetails, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'move_left':
                self.core.keybindings.set_simulating(True)
                key = super(ContactDetails, self).keypress(size, 'left')
                self.core.keybindings.set_simulating(False)
                return key
            case 'add_gift':
                focused_contact = self.core.frame.contact_list \
                    .get_focused_contact()
                self.core.cli.add_gift(focused_contact)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class ListEntry(urwid.Button):
    def __init__(self, label, pos, core):
        super(ListEntry, self).__init__(label)
        self.core = core
        self.pos = pos
        self.set_label(label)

    def set_label(self, label):
        super(ListEntry, self).set_label(label)
        cursor_pos = len(label) + 1
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            label, cursor_pos), None, 'selected')


class ContactEntry(ListEntry):
    def __init__(self, contact, pos, core):
        super(ContactEntry, self).__init__(contact.name, pos, core)
        self.name = 'contact_entry'
        self.contact = contact

    def keypress(self, size, key):
        if key == 'enter':
            self.core.keybindings.set_simulating(True)
            key = super(ContactEntry, self).keypress(size, 'right')
            self.core.keybindings.set_simulating(False)
            return key

        key = super(ContactEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'rename_contact':
                self.core.cli.rename_contact(self.contact)
            case 'delete_contact':
                self.core.cli.delete_contact(self.contact)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class DetailEntry(ListEntry):
    def __init__(self, contact, detail, label, pos, core):
        super(DetailEntry, self).__init__(label, pos, core)
        self.contact = contact
        self.detail = detail


class AttributeEntry(DetailEntry):
    def __init__(self, contact, attribute, pos, core):
        label = attribute.key + ': ' + attribute.value
        super(AttributeEntry, self).__init__(contact, attribute, label, pos,
                                             core)
        self.attribute = attribute
        self.name = 'attribute_entry'

    def keypress(self, size, key):
        key = super(DetailEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'edit_attribute':
                self.core.cli.edit_attribute(self.contact, self.attribute)
            case 'delete_attribute':
                self.core.cli.delete_attribute(self.contact, self.attribute)
            case 'copy_attribute':
                pyperclip.copy(self.attribute.value)
                msg = "Copied \"" + self.attribute.value + "\" to clipboard."
                self.core.frame.console.show_message(msg)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class GiftEntry(DetailEntry):
    def __init__(self, contact, gift, pos, core):
        super(GiftEntry, self).__init__(contact, gift, gift.name, pos, core)
        self.gift = gift
        self.name = 'gift_entry'

    def keypress(self, size, key):
        key = super(GiftEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'edit_gift':
                self.core.cli.edit_gift(self.contact, self.gift)
            case 'delete_gift':
                self.core.cli.delete_gift(self.contact, self.gift)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class NoteEntry(DetailEntry):
    def __init__(self, contact, note, pos, core):
        super(NoteEntry, self).__init__(contact, note, note.content, pos, core)
        self.note = note
        self.name = 'note_entry'

    def keypress(self, size, key):
        if key == 'enter':
            self.core.cli.edit_note(self.contact, self.note)
            return

        key = super(NoteEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'edit_note':
                self.core.cli.edit_note(self.contact, self.note)
            case 'rename_note':
                self.core.cli.rename_note(self.contact, self.note)
            case 'delete_note':
                self.core.cli.delete_note(self.contact, self.note)
            case 'encrypt_note':
                self.core.cli.encrypt_note(self.contact, self.note)
            case 'toggle_note_encryption':
                self.core.cli.toggle_note_encryption(self.contact, self.note)
            case 'show_all_encrypted_notes':
                self.core.cli.show_all_encrypted_notes(self.contact)
            case 'hide_all_encrypted_notes':
                self.core.cli.hide_all_encrypted_notes(self.contact)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class EncryptedNoteEntry(DetailEntry):
    def __init__(self, contact, note, pos, core, visible=False):
        if visible:
            content = '[' + note.content + ']'
            super(EncryptedNoteEntry, self).__init__(contact, note, content,
                                                     pos, core)
        else:
            super(EncryptedNoteEntry, self).__init__(contact, note,
                                                     '(encrypted)', pos, core)
        self.note = note
        self.name = 'note_entry'

    def keypress(self, size, key):
        key = super(EncryptedNoteEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'edit_note':
                self.core.cli.edit_note(self.contact, self.note)
            case 'rename_note':
                self.core.cli.rename_note(self.contact, self.note)
            case 'delete_note':
                self.core.cli.delete_note(self.contact, self.note)
            case 'encrypt_note':
                self.core.cli.encrypt_note(self.contact, self.note)
            case 'decrypt_note':
                self.core.cli.decrypt_note(self.contact, self.note)
            case 'toggle_note_encryption':
                self.core.cli.toggle_note_encryption(self.contact, self.note)
            case 'show_all_encrypted_notes':
                self.core.cli.show_all_encrypted_notes(self.contact)
            case 'hide_all_encrypted_notes':
                self.core.cli.hide_all_encrypted_notes(self.contact)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class GoogleNoteEntry(DetailEntry):
    def __init__(self, contact, note, pos, core):
        super(GoogleNoteEntry, self).__init__(contact, note, note.content, pos,
                                              core)
        self.note = note


class GoogleAttributeEntry(DetailEntry):
    def __init__(self, contact, attribute, pos, core):
        label = 'G: ' + attribute.key + ': ' + attribute.value
        super(GoogleAttributeEntry, self).__init__(contact, attribute, label,
                                                   pos, core)
        self.attribute = attribute
        self.name = 'attribute_entry'

    def keypress(self, size, key):
        key = super(GoogleAttributeEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            # case 'edit_attribute':
            #     self.core.cli.edit_attribute(self.contact, self.attribute)
            # case 'delete_attribute':
            #     self.core.cli.delete_attribute(self.contact, self.attribute)
            case 'copy_attribute':
                pyperclip.copy(self.attribute.value)
                msg = "Copied \"" + self.attribute.value + "\" to clipboard."
                self.core.frame.console.show_message(msg)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class Console(urwid.Filler):
    def __init__(self, core):
        super(Console, self).__init__(urwid.Text(""))
        self.core = core
        self.name = 'console'
        self.filter_mode = False

    def show_console(self, command=''):
        self.body = urwid.Edit(":", command)
        self.core.frame.set_focus('footer')

    def show_message(self, message):
        self.body = urwid.Text(message)

    def show_input(self, request):
        self.body = urwid.Edit("{}?".format(request))
        self.core.frame.set_focus('footer')

    def show_search(self):
        self.body = urwid.Edit("/")
        self.core.frame.set_focus('footer')

    def show_filter(self, command):
        self.filter_mode = True
        self.show_console(command)

    def show_passphrase_input(self):
        self.body = urwid.Edit("Passphrase: ", mask="*")
        self.core.frame.set_focus('footer')

    def show_meta(self, meta):
        self.body = urwid.AttrMap(urwid.Text(meta, 'right'), 'status_bar')

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
                self.core.cli.unfilter_contacts()
                self.core.frame.clear_footer()
            elif key == 'enter':
                self.filter_mode = False
                args = self.original_widget.edit_text.split()
                return self.core.cli.handle(False)
            else:
                super(Console, self).keypress(size, key)
                args = self.original_widget.edit_text.split()
                return self.core.cli.handle(args)
        else:
            if key == 'esc':
                self.core.frame.clear_footer()
            elif key == 'enter':
                args = self.original_widget.edit_text.split()
                return self.core.cli.handle(args)
            else:
                return super(Console, self).keypress(size, key)
