from datetime import date,datetime
import urwid

from objects import *
from cli import *


class ContactLoop(urwid.MainLoop):
    def __init__(self, frame, config):
        palette = config['display']['palette']
        loop = urwid.MainLoop(frame, palette, unhandled_input=self.show_or_exit)
        loop.run()

    def show_or_exit(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()


class ContactFrame(urwid.Frame):
    def __init__(self, config, core):
        super(ContactFrame, self).__init__(None)
        self.config = config
        self.core = core
        self.first_detail_pos = 2
        self.current_contact = None
        self.current_contact_pos = None
        self.current_detail = None
        self.current_detail_pos = None
        self.core.find_mode = False
        self.core.filter_mode = False
        self.set_footer()

    def init_contact_list(self, contact_list):
        self.body = ContactFrameColumns(self.core, self.config)
        self.set_contact_list(contact_list)
        self.set_contact_details()
        self.watch_focus()

    def set_contact_list(self, contact_list):
        self.body.set_contact_list(contact_list)
        self.contact_list = self.body.contents[0][0].base_widget

    def set_contact_details(self, contact=None):
        if contact is None:
            contact = self.contact_list.get_focused_contact()
        contact.get_details() # augment existing contact with details (not before for performance)
        self.body.set_contact_details(contact)
        self.contact_details = self.body.contents[-1][0].base_widget

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
            self.set_contact_list(contact_list)
        self.set_contact_details(contact)
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
            contact_pos = min(self.current_contact_pos, len(self.contact_list.body) - 1)
            detail_pos = 0
        elif action is Action.DETAIL_ADDED_OR_EDITED:
            detail_pos = self.contact_details.get_detail_position(detail)
            self.body.set_focus_column(1)
        elif action is Action.DETAIL_DELETED:
            if contact.has_details(): # don't focus details column if contact has no details
                detail_pos = min(self.current_detail_pos, len(self.contact_details.body) - 1)
                self.body.set_focus_column(1)
            else:
                detail_pos = 0
        elif action is Action.FILTERING or action is Action.FILTERED:
            contact_pos = self.contact_list.get_contact_position(self.current_contact)
            detail_pos = 0
        elif action is Action.REFRESH:
            contact_pos = self.contact_list.get_contact_position(self.current_contact)
            detail_pos = 0
        else: # defaults
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
        #hiea = "{} {}".format(str(self.current_contact_pos), str(self.current_detail_pos))
        #self.console.show_meta(hiea)

    def set_header(self):
        pass

    def set_footer(self):
        self.footer = urwid.BoxAdapter(Console(self.core), height=1)
        self.console = self.footer.original_widget

    def clear_footer(self):
        self.footer = urwid.BoxAdapter(Console(self.core), height=1)
        self.console = self.footer.original_widget
        self.set_focus('body')

    def details_focused(self):
        return self.body.get_focus_column() == 1


class ContactFrameColumns(urwid.Columns):
    def __init__(self, core, config):
        self.core = core
        self.focus_map = config['display']['focus_map']
        self.nav_width = config['display']['nav_width']
        super(ContactFrameColumns, self).__init__([], dividechars=1)

    def set_contact_list(self, contact_list):
        column = (urwid.AttrMap(ContactList(contact_list, self.core),
            'options', self.focus_map), self.options('given', self.nav_width))
        if len(self.contents) < 1:
            self.contents.append(column)
        else:
            self.contents[0] = column

    def set_contact_details(self, contact):
        column = (urwid.AttrMap(ContactDetails(contact, self.core),
            'options', self.focus_map), self.options('weight', 1, True))
        if len(self.contents) < 2:
            self.contents.append(column)
        else:
            self.contents[1] = column

    def keypress(self, size, key):
        if key == 'ctrl r':
            self.core.frame.watch_focus()
            self.core.frame.refresh_contact_list(Action.REFRESH, None, None,
                    self.core.filter_string)
        else:
            return super(ContactFrameColumns, self).keypress(size, key)

    

class CustListBox(urwid.ListBox):
    def __init__(self, listwalker, core):
        super(CustListBox, self).__init__(listwalker)
        self.repeat_command = 0
        self.core = core

    def keypress(self, size, key):
        self.core.frame.watch_focus()

        if key == 'esc':
            self.core.last_keypress = None
            self.core.find_mode = False
            self.core.find_string = ''
        elif self.core.find_mode is True:
            if key == 'enter':
                self.core.find_mode = False
                self.core.find_string = ''
            else:
                self.core.find_string += str(key)
                found = self.core.frame.contact_list.jump_to_contact(self.core.find_string)
                # workaround, otherwise list focus not updated
                super(CustListBox, self).keypress(size, 'left')
                if not found:
                    self.core.find_mode = False
                    self.core.find_string = ''
        elif self.core.last_keypress == 'i':
            focused_contact = self.core.frame.contact_list.get_focused_contact()
            if key == 'i':
                self.core.last_keypress = None
                self.core.cli.add_attribute(focused_contact)
            elif key == 'g':
                self.core.last_keypress = None
                self.core.cli.add_google_contact()
#            elif key == 'g':
#                self.core.last_keypress = None
#                self.core.cli.add_gift(focused_contact)
            elif key == 'n':
                self.core.last_keypress = None
                self.core.cli.add_note(focused_contact)
            elif key == 'e':
                self.core.last_keypress = None
                self.core.cli.add_encrypted_note(focused_contact)
            else:
                self.core.last_keypress = None
        elif self.core.last_keypress == 'g':
            if key == 'g':
                self.core.last_keypress = None
                # 2x as workaround, otherwise list focus not updated
                super(CustListBox, self).keypress(size, 'home')
                super(CustListBox, self).keypress(size, 'home')
            else:
                self.core.last_keypress = None
        elif self.core.last_keypress == 'z':
            if key == 'z':
                self.core.last_keypress = None
                self.core.cli.filter_contacts()
            else:
                self.core.last_keypress = None
        elif key == 'I':
            self.core.cli.add_contact()
        else:
            if key == 'i':
                self.core.last_keypress = 'i'
            elif key == '/':
                self.core.cli.search_contact()
            elif key == 'f':
                self.core.find_mode = True
                self.core.find_string = ''
            elif key == 't':
                if self.repeat_command > 0:
                    self.jump_down(size, self.repeat_command)
                    self.repeat_command = 0
                else:
                    super(CustListBox, self).keypress(size, 'down')
            elif key == 'r':
                if self.repeat_command > 0:
                    self.jump_up(size, self.repeat_command)
                    self.repeat_command = 0
                else:
                    super(CustListBox, self).keypress(size, 'up')
            elif key == 'G':
                # 2x as workaround, otherwise list focus not updated
                super(CustListBox, self).keypress(size, 'end')
                super(CustListBox, self).keypress(size, 'end')
            elif key == 'g':
                self.core.last_keypress = 'g'
            elif key == 'z':
                self.core.last_keypress = 'z'
            elif key == 'Z':
                self.core.cli.unfilter_contacts()
            elif key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if self.repeat_command > 0:
                    self.repeat_command = int(str(self.repeat_command) + key)
                else:
                    self.repeat_command = int(key)
            else:
                return super(CustListBox, self).keypress(size, key)

    def jump_down(self, size, n):
        for i in range(0, n):
            super(CustListBox, self).keypress(size, 'down')

    def jump_up(self, size, n):
        for i in range(0, n):
            super(CustListBox, self).keypress(size, 'up')


class ContactList(CustListBox):
    def __init__(self, contact_list, core):
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactList, self).__init__(listwalker, core)
        self.core = core
        self.set(contact_list)

    def set(self, contact_list):
        a = []
        pos = 0
        for c in contact_list:
            entry = ContactEntry(c, pos, self.core)
            urwid.connect_signal(entry, 'click', self.core.frame.set_contact_details) #TODO in ListEntry
            a.append(entry)
            pos = pos + 1
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, 'modified', self.core.frame.set_contact_details)

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
        if self.core.last_keypress is None and self.core.find_mode is False:
            if key == 'n':
                # if has details
                #if self.core.frame.contact_details.number_of_details() > 0:
                return super(ContactList, self).keypress(size, 'right')
                #else:
                #    return super(ContactList, self).keypress(size, key)
            else:
                return super(ContactList, self).keypress(size, key)
        else:
            return super(ContactList, self).keypress(size, key)


class ContactDetails(CustListBox):
    def __init__(self, contact, core):
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactDetails, self).__init__(listwalker, core)
        self.core = core
        self.set(contact)

    def set(self, contact):
        name = DetailEntry(contact, Name(contact.name), contact.name, 0, self.core)
        entries = [name, urwid.Divider()]
        pos = len(entries)

        if contact.attributes is not None:
            for a in contact.attributes:
                entries.append(AttributeEntry(contact, Attribute(a[0], a[1]), pos, self.core))
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

        if contact.notes is not None:
            if len(entries) > 2:
                entries.append(urwid.Divider())
                pos = pos + 1
            entries.append(urwid.Text(u"NOTIZEN"))
            pos = pos + 1
            for note in contact.notes:
                if type(note) is Note: # plain note
                    entries.append(NoteEntry(contact, note, pos, self.core))
                else: # encrypted note
                    # check if made visible
                    if contact.has_visible_note(note):
                        visible_note = contact.get_visible_note(note)
                        entries.append(EncryptedNoteEntry(contact, visible_note, pos, self.core, visible=True))
                    else:
                        entries.append(EncryptedNoteEntry(contact, note, pos, self.core))
                pos = pos + 1

        self.body = urwid.SimpleFocusListWalker(entries)
        urwid.connect_signal(self.body, 'modified', self.show_meta)

    def show_meta(self):
        if self.core.frame.details_focused() is True:
            if type(self.focus) is NoteEntry or type(self.focus) is EncryptedNoteEntry:
                date = datetime.strftime(self.focus.note.date, '%d-%m-%Y')
                self.core.frame.console.show_meta(date)
            elif isinstance(self.focus, DetailEntry):
                self.core.frame.console.show_meta("")
                #self.core.frame.console.show_meta(str(self.focus.pos))
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
        try: # fix for frequent problem: # TODO undo this after improving get_detail_position()
            # "'<' not supported between instances of 'NoneType' and 'int'"
            self.focus_position = pos
        except TypeError:
            pass


    def get_detail_position(self, detail):
        pos = 0
        for entry in self.body:
            if isinstance(entry, DetailEntry):
                # TODO Workaround for gifts (as they are not recognized as gifts when creating them with add-attribute instead of add-gift
                if isinstance(detail, Attribute) and detail.key == "giftIdea" and isinstance(entry.detail, Gift):
                    if detail.value == entry.detail.name:
                        return pos
                else:
                    if type(entry.detail) == type(detail):
                        if entry.detail == detail:
                            return pos
            pos = pos + 1
        return None

    def keypress(self, size, key):
        if key == 'd':
            return super(ContactDetails, self).keypress(size, 'left')
        else:
            return super(ContactDetails, self).keypress(size, key)


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
        self.contact = contact

    def keypress(self, size, key):
        if self.core.last_keypress is None:
            if key == 'a':
                self.core.cli.rename_contact(self.contact)
            elif key == 'h':
                self.core.cli.delete_contact(self.contact)
            elif key == 'enter':
                return super(ContactEntry, self).keypress(size, 'right')
            else:
                return super(ContactEntry, self).keypress(size, key)
        else:
            return super(ContactEntry, self).keypress(size, key)


class DetailEntry(ListEntry):
    def __init__(self, contact, detail, label, pos, core):
        super(DetailEntry, self).__init__(label, pos, core)
        self.contact = contact
        self.detail = detail


class AttributeEntry(DetailEntry):
    def __init__(self, contact, attribute, pos, core):
        label = attribute.key + ': ' + attribute.value
        super(AttributeEntry, self).__init__(contact, attribute, label, pos, core)
        self.attribute = attribute

    def keypress(self, size, key):
        if key == 'a':
            self.core.cli.edit_attribute(self.contact, self.attribute)
        elif key == 'h':
            self.core.cli.delete_attribute(self.contact, self.attribute)
        elif key == 'y':
            pyperclip.copy(self.attribute.value)
            msg = "Copied \"" + self.attribute.value + "\" to clipboard."
            self.core.frame.console.show_message(msg)
        else:
            return super(ListEntry, self).keypress(size, key)

class GiftEntry(DetailEntry):
    def __init__(self, contact, gift, pos, core):
        super(GiftEntry, self).__init__(contact, gift, gift.name, pos, core)
        self.gift = gift

    def keypress(self, size, key):
        if key == 'a':
            self.core.cli.edit_gift(self.contact, self.gift)
        elif key == 'h':
            self.core.cli.delete_gift(self.contact, self.gift)
        else:
            return super(GiftEntry, self).keypress(size, key)

class NoteEntry(DetailEntry):
    def __init__(self, contact, note, pos, core):
        super(NoteEntry, self).__init__(contact, note, note.content, pos, core)
        self.note = note

    def keypress(self, size, key):
        if self.core.last_keypress is None:
            if key == 'enter':
                self.core.cli.edit_note(self.contact, self.note)
            elif key == 'a':
                self.core.cli.rename_note(self.contact, self.note)
            elif key == 'h':
                self.core.cli.delete_note(self.contact, self.note)
            elif key == 'e':
                self.core.last_keypress = 'e'
            else:
                return super(NoteEntry, self).keypress(size, key)
        elif self.core.last_keypress == 'e':
            if key == 'e':
                self.core.cli.encrypt_note(self.contact, self.note)
                self.core.last_keypress = None
            elif key == 'v':
                self.core.cli.toggle_note_encryption(self.contact, self.note)
                self.core.last_keypress = None
            elif key == 's':
                self.core.cli.show_all_encrypted_notes(self.contact)
                self.core.last_keypress = None
            elif key == 'h':
                self.core.cli.hide_all_encrypted_notes(self.contact)
                self.core.last_keypress = None
            else:
                self.core.last_keypress = None

class EncryptedNoteEntry(DetailEntry):
    def __init__(self, contact, note, pos, core, visible=False):
        if visible:
            content = '[' + note.content + ']'
            super(EncryptedNoteEntry, self).__init__(contact, note, content, pos, core)
        else:
            super(EncryptedNoteEntry, self).__init__(contact, note, '(encrypted)', pos, core)
        self.note = note

    def keypress(self, size, key):
        if self.core.last_keypress is None:
            if key == 'enter':
                self.core.cli.edit_note(self.contact, self.note)
            elif key == 'a':
                self.core.cli.rename_note(self.contact, self.note)
            elif key == 'h':
                self.core.cli.delete_note(self.contact, self.note)
            elif key == 'e':
                self.core.last_keypress = 'e'
            else:
                return super(EncryptedNoteEntry, self).keypress(size, key)
        elif self.core.last_keypress == 'e':
            if key == 'left': # 'd' is mapped to 'left'
                self.core.cli.decrypt_note(self.contact, self.note)
                self.core.last_keypress = None
            elif key == 'e':
                self.core.cli.encrypt_note(self.contact, self.note)
                self.core.last_keypress = None
            elif key == 'v':
                self.core.cli.toggle_note_encryption(self.contact, self.note)
                self.core.last_keypress = None
            elif key == 's':
                self.core.cli.show_all_encrypted_notes(self.contact)
                self.core.last_keypress = None
            elif key == 'h':
                self.core.cli.hide_all_encrypted_notes(self.contact)
                self.core.last_keypress = None
            else:
                self.core.last_keypress = None

class GoogleAttributeEntry(DetailEntry):
    def __init__(self, contact, attribute, pos, core):
        label = 'G: ' + attribute.key + ': ' + attribute.value
        super(GoogleAttributeEntry, self).__init__(contact, attribute, label, pos, core)
        self.attribute = attribute

    def keypress(self, size, key):
        #if key == 'a':
        #    self.core.cli.edit_attribute(self.contact, self.attribute)
        #elif key == 'h':
        #    self.core.cli.delete_attribute(self.contact, self.attribute)
        if key == 'y':
            pyperclip.copy(self.attribute.value)
            msg = "Copied \"" + self.attribute.value + "\" to clipboard."
            self.core.frame.console.show_message(msg)
        else:
            return super(ListEntry, self).keypress(size, key)


class Console(urwid.Filler):
    def __init__(self, core):
        super(Console, self).__init__(urwid.Text(""))
        self.core = core
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
