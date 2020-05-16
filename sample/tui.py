from datetime import date,datetime
import urwid
import pudb


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

    def set_contact_list(self, contact_list):
        focus_map = self.config['display']['focus_map']
        self.body = ContactFrameColumns(contact_list, self, self.config)
        self.set_contact_details()

    def set_contact_details(self):
        contact = self.get_focused_contact()
        contact.get_details() # augment existing contact with details (not before for performance)
        if len(self.body.contents) > 1:
            del self.body.contents[1]
        self.body.set_contact_details(contact)

    def refresh_contact_list(self):
        focused_contact = self.get_focused_contact()

        contact_list = self.core.get_all_contacts()
        self.set_contact_list(contact_list)

        self.set_focused_contact(focused_contact)

    def set_contact_detail_meta(self, meta):
        pass
        #text = urwid.AttrMap(urwid.Text(meta, 'right'), 'status_bar')
        #self.set_footer(text)

    def set_footer(self):
        pass

    def clear_footer(self):
        pass

    def set_header(self):
        pass

    def get_focused_contact(self):
        entry = self.body.contents[0][0].base_widget.get_focus()
        return entry.contact

    def set_focused_contact(self, contact):
        pos = self.body.contents[0][0].base_widget.get_contact_position(contact)
        self.body.contents[0][0].base_widget.set_focus(pos)



class ContactFrameColumns(urwid.Columns):
    def __init__(self, contact_list, frame, config):
        self.frame = frame
        self.focus_map = config['display']['focus_map']
        self.nav_width = config['display']['nav_width']
        super(ContactFrameColumns, self).__init__([], dividechars=1)
        self.set_contact_list(contact_list)

    def set_contact_list(self, contact_list):
        self.contents.append((urwid.AttrMap(ContactList(contact_list, self.frame),
            'options', self.focus_map), self.options('given', self.nav_width)))

    def set_contact_details(self, contact):
        self.contents.append((urwid.AttrMap(ContactDetails(contact, self.frame),
            'options', self.focus_map), self.options('weight', 1, True)))
#        contact_details = ContactDetails(contact, self.frame),
#        attr_map = urwid.AttrMap(contact_details, 'options', self.focus_map)
#        self.contents.append((attr_map, self.options('weight', 1, True)))

    def keypress(self, size, key):
        if key == 'ctrl r':
            self.frame.refresh_contact_list()
        else:
            return super(ContactFrameColumns, self).keypress(size, key)

    

class CustListBox(urwid.ListBox):
    def __init__(self, listwalker):
        super(CustListBox, self).__init__(listwalker)
        self.repeat_command = 0

    def keypress(self, size, key):
        if key == 't':
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
            super(CustListBox, self).keypress(size, 'end')
            super(CustListBox, self).keypress(size, 'end')
        elif key == 'g':
            super(CustListBox, self).keypress(size, 'home')
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
    def __init__(self, contact_list, frame):
        listwalker = urwid.SimpleFocusListWalker([])
        self.frame = frame
        super(ContactList, self).__init__(listwalker)
        self.set(contact_list)

    def set(self, contact_list):
        a = []
        for c in contact_list:
            entry = ContactEntry(c)
            urwid.connect_signal(entry, 'click', self.frame.set_contact_details) #TODO in ListEntry
            a.append(entry)
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, 'modified', self.frame.set_contact_details)

    def get_focus(self):
        return self.focus

    def get_contact_position(self, contact):
        pos = 0
        for entry in self.body:
            if entry.label.startswith(contact.name):
                return pos
            pos = pos + 1
        return None

    def keypress(self, size, key):
        if key == 'n':
            return super(ContactList, self).keypress(size, 'right')
        else:
            return super(ContactList, self).keypress(size, key)


class ContactDetails(CustListBox):
    def __init__(self, contact, frame):
        listwalker = urwid.SimpleFocusListWalker([])
        self.frame = frame
        super(ContactDetails, self).__init__(listwalker)
        self.set(contact)

    def set(self, contact):
        entries = []

        entries.append(AttributeEntry(contact, "givenName", contact.name))
        entries.append(urwid.Divider())

        if contact.attributes is not None:
            for a in contact.attributes:
                entries.append(AttributeEntry(contact, a[0], a[1]))

        if contact.gifts is not None:
            if len(entries) > 2:
                entries.append(urwid.Divider())
            entries.append(urwid.Text(u"GESCHENKE"))
            for a in contact.gifts:
                entries.append(GiftEntry(contact, a))

        if contact.notes is not None:
            if len(entries) > 2:
                entries.append(urwid.Divider())
            entries.append(urwid.Text(u"NOTIZEN"))
            for d, content in contact.notes.items():
                date_obj = datetime.strptime(d, '%Y%m%d')
                date = datetime.strftime(date_obj, '%d-%m-%Y')
                entries.append(NoteEntry(contact, date, content))

        self.body = urwid.SimpleFocusListWalker(entries)
        urwid.connect_signal(self.body, 'modified', self.show_meta)

    def hide(self):
        pass

    def set_focus(self, contact):
        pass

    def show_meta(self):
        if isinstance(self.focus, NoteEntry):
            self.frame.set_contact_detail_meta(self.focus.date)
        else:
            self.frame.clear_footer()

    def keypress(self, size, key):
        if key == 'd':
            return super(ContactDetails, self).keypress(size, 'left')
        else:
            return super(ContactDetails, self).keypress(size, key)


class ListEntry(urwid.Button):
    def __init__(self, caption):
        super(ListEntry, self).__init__(caption)
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, 100), None, 'selected')  #TODO cursor position


class ContactEntry(ListEntry):
    def __init__(self, contact):
        super(ContactEntry, self).__init__(contact.name)
        self.contact = contact


class DetailEntry(ListEntry):
    def __init__(self, contact, label):
        super(DetailEntry, self).__init__(label)
        self.contact = contact


class AttributeEntry(DetailEntry):
    def __init__(self, contact, key, value):
        label = key + ': ' + value
        super(AttributeEntry, self).__init__(contact, label)

    def keypress(self, size, key):
        if key == 'i':
            command_add_attribute(self.contact, self)
        elif key == 'a':
            command_edit_attribute(self.contact, self)
        elif key == 'h':
            command_delete_attribute(self.contact, self)
        elif key == 'y':
            pyperclip.copy(self.value)
            fill.show_message("Copied \"" + self.value + "\" to clipboard.")
        else:
            return super(ListEntry, self).keypress(size, key)

class GiftEntry(DetailEntry):
    def __init__(self, contact, gift):
        super(GiftEntry, self).__init__(contact, gift)

class NoteEntry(DetailEntry):
    def __init__(self, contact, date, note):
        self.date = date
        super(NoteEntry, self).__init__(contact, note)

class Console():
    pass
