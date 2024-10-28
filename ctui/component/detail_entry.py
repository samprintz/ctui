import pyperclip

from ctui.commands import EditAttribute, DeleteAttribute, RenameGift, EditGift
from ctui.component.list_entry import CListEntry


class DetailEntry(CListEntry):
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
                command = f'{EditAttribute.name} {self.attribute.key} {self.attribute.value}'
                self.core.ui.console.show_console(command)
            case 'delete_attribute':
                command = f'{DeleteAttribute.name} {self.attribute.key} {self.attribute.value}'
                self.core.ui.console.show_console(command)
            case 'copy_attribute':
                pyperclip.copy(self.attribute.value)
                msg = "Copied \"" + self.attribute.value + "\" to clipboard."
                self.core.ui.console.show_message(msg)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class GiftEntry(DetailEntry):
    def __init__(self, contact, gift, pos, core):
        label = ''

        if gift.gifted:
            label += 'x '

        if gift.permanent:
            label += '+ '

        label += gift.name

        if gift.occasions:
            label += f' ({', '.join(gift.occasions)})'

        super(GiftEntry, self).__init__(contact, gift, label, pos, core)
        self.gift = gift
        self.name = 'gift_entry'

    def keypress(self, size, key):
        if key == 'enter':  # TODO special treatment of enter (must be calling super())
            EditGift(self.core).execute(self.gift.name)
            return

        key = super(GiftEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'rename_gift':
                command = f'{RenameGift.name} {self.gift.name}'
                self.core.ui.console.show_console(command)
            case 'delete_gift':
                command = f'{DeleteGift.name} {self.gift.name}'  # TODO implement DeleteGift in commands.py
                self.core.ui.console.show_console(command)
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
        if key == 'enter':  # TODO special treatment of enter (must be calling super())
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
                self.core.ui.console.show_message(msg)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
