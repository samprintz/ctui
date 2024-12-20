from datetime import datetime, date

import urwid

from ctui.commands import AddAttribute, AddNote, AddEncryptedNote
from ctui.commands import AddGift
from ctui.component.detail_entry import DetailEntry, AttributeEntry, \
    GoogleAttributeEntry, GiftEntry, GoogleNoteEntry, NoteEntry, \
    EncryptedNoteEntry
from ctui.component.list_box import CListBox
from ctui.model.attribute import Attribute
from ctui.model.gift import Gift
from ctui.model.note import Note


class ContactDetails(CListBox):
    def __init__(self, entries, core, name):
        self.core = core
        listwalker = urwid.SimpleFocusListWalker([])
        super(ContactDetails, self).__init__(listwalker, core, name)

        self.body = urwid.SimpleFocusListWalker(entries)
        urwid.connect_signal(self.body, 'modified', self.show_meta)

    def show_meta(self):
        if type(self.focus) is NoteEntry or type(
                self.focus) is EncryptedNoteEntry:
            date = datetime.strptime(self.focus.note.note_id, '%Y%m%d')
            date_str = datetime.strftime(date, '%d-%m-%Y')
            self.core.ui.console.show_meta(date_str)
        elif isinstance(self.focus, DetailEntry):
            self.core.ui.console.show_meta("")
            # self.core.ui.console.show_meta(str(self.focus.pos))

    def get_focused_detail(self):
        if not hasattr(self.focus, 'detail'):
            return None
        return self.focus.detail

    def get_focus_position(self):
        if len(self.contents) > 0:
            return self.focus_position

    def set_focus_position(self, pos):
        try:  # fix for frequent problem: # TODO undo this after improving get_detail_position()
            # "'<' not supported between instances of 'NoneType' and 'int'"
            if len(self.contents) > 0:
                self.focus_position = pos
        except TypeError:
            pass

    def get_count(self) -> int:
        count = 0
        for entry in self.body:
            if type(entry) is AttributeEntry or type(
                    entry) is NoteEntry or type(entry) is GiftEntry:
                count = count + 1
        return count

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


class AttributeDetails(ContactDetails):
    def __init__(self, contact_id, core):
        self.core = core
        self.name = 'contact_attribute_details'

        attributes = self.core.rdfstore.get_attributes(contact_id)
        google_attributes = []  # TODO load Google attributes

        entries = []
        pos = 0

        for attribute in attributes:
            entries.append(AttributeEntry(contact_id,
                                          # TODO use Attribute directly?
                                          Attribute(attribute[0], attribute[1]),
                                          pos,
                                          self.core)
                           )
            pos = pos + 1

        for attribute in google_attributes:
            entries.append(
                GoogleAttributeEntry(contact_id, attribute, pos, self.core))
            pos = pos + 1

        super(AttributeDetails, self).__init__(entries, core,
                                             'contact_details_attribute')

    def keypress(self, size, key):
        key = super(ContactDetails, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'add_attribute':
                command = f'{AddAttribute.name} '
                self.core.ui.console.show_console(command)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class GiftDetails(ContactDetails):
    def __init__(self, contact_id, core):
        self.core = core
        self.name = 'contact_gift_details'

        gifts = self.core.textfilestore.get_gifts(contact_id)
        gifts_sorted = sorted(gifts, key=lambda g: (
            g.gifted and not g.permanent,
            g.name.lower()
        ))

        entries = []
        pos = 0

        for gift in gifts_sorted:
            if isinstance(gift, Gift):
                entries.append(GiftEntry(contact_id, gift, pos, self.core))
            else:
                entries.append(
                    DetailEntry(contact_id, gift, gift.name, pos, self.core))
            pos = pos + 1

        super(GiftDetails, self).__init__(entries, core,
                                          'contact_details_gifts')

    def keypress(self, size, key):
        key = super(ContactDetails, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'add_attribute':
                command = f'{AddGift.name} '
                self.core.ui.console.show_console(command)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class NoteDetails(ContactDetails):
    def __init__(self, contact_id, core):
        self.core = core
        self.name = 'contact_note_details'

        notes = self.core.textfilestore.get_notes(contact_id)
        google_notes = []  # TODO load Google attributes

        entries = []
        pos = 0

        for note in notes:
            if type(note) is Note:  # plain note
                entries.append(
                    NoteEntry(contact_id, note, pos, self.core))
            else:  # encrypted note
                # check if made visible
                if self.core.memorystore.has_note(
                        contact_id, note.note_id):
                    visible_note = self.core.memorystore.get_note(
                        contact_id, note.note_id)
                    entries.append(
                        EncryptedNoteEntry(contact_id, visible_note, pos,
                                           self.core, visible=True))
                else:
                    entries.append(
                        EncryptedNoteEntry(contact_id, note, pos, self.core))
            pos = pos + 1

        for note in google_notes:
            entries.append(GoogleNoteEntry(contact_id, note, pos, self.core))
            pos = pos + 1

        super(NoteDetails, self).__init__(entries, core,
                                          'contact_details_notes')

    def keypress(self, size, key):
        key = super(ContactDetails, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'add_attribute':
                note_id = datetime.strftime(date.today(), "%Y%m%d")
                command = f'{AddNote.name} {note_id}'
                self.core.ui.console.show_console(command)
            case 'add_encrypted_note':
                note_id = datetime.strftime(date.today(), "%Y%m%d")
                command = f'{AddEncryptedNote.name} {note_id}'
                self.core.ui.console.show_console(command)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
