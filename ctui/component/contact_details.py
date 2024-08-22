import urwid
from datetime import datetime

from ctui.component.detail_entry import DetailEntry, AttributeEntry, \
    GoogleAttributeEntry, GiftEntry, GoogleNoteEntry, NoteEntry, \
    EncryptedNoteEntry
from ctui.component.list_box import CListBox

from ctui.objects import Name, Attribute, Gift, Note, GoogleContact


class ContactDetails(CListBox):
    def __init__(self, core):
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactDetails, self).__init__(listwalker, core,
                                             'contact_details')
        self.core = core

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
