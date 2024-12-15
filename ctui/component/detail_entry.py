import pyperclip

from ctui.commands import EditAttribute, DeleteAttribute, RenameGift, EditGift, \
    EditNote, RenameNote, DeleteNote, DeleteGift, EncryptNote, DecryptNote, \
    ToggleNoteEncryption, ShowAllEncryptedNotes, HideAllEncryptedNotes
from ctui.component.list_entry import CListEntry


class DetailEntry(CListEntry):
    def __init__(self, contact_id, detail, label, pos, core):
        super(DetailEntry, self).__init__(label, pos, core)
        self.contact_id = contact_id
        self.detail = detail


class AttributeEntry(DetailEntry):
    def __init__(self, contact_id, attribute, pos, core):
        label = attribute.key + ': ' + attribute.value
        super(AttributeEntry, self).__init__(contact_id, attribute, label, pos,
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
    def __init__(self, contact_id, gift, pos, core):
        label = ''

        if gift.gifted:
            label += 'x '

        if gift.permanent:
            label += '+ '

        label += gift.name

        if gift.occasions:
            label += f' ({', '.join(gift.occasions)})'

        super(GiftEntry, self).__init__(contact_id, gift, label, pos, core)
        self.gift = gift
        self.name = 'gift_entry'

    def keypress(self, size, key):
        if key == 'enter':  # TODO special treatment of enter (must be calling super())
            EditGift(self.core).execute([self.gift.name])
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
                command = f'{DeleteGift.name} {self.gift.name}'
                self.core.ui.console.show_console(command)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class NoteEntry(DetailEntry):
    def __init__(self, contact_id, note, pos, core):
        super(NoteEntry, self).__init__(contact_id, note, note.content, pos,
                                        core)
        self.note = note
        self.name = 'note_entry'

    def keypress(self, size, key):
        if key == 'enter':  # TODO special treatment of enter (must be calling super())
            EditNote(self.core).execute([self.note.note_id])
            return

        key = super(NoteEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        match command_id:
            case 'edit_note':
                command = f'{EditNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'rename_note':
                command = f'{RenameNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'delete_note':
                command = f'{DeleteNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'encrypt_note':
                EncryptNote(self.core).execute([self.note.note_id])
            case 'show_all_encrypted_notes':
                ShowAllEncryptedNotes(self.core).execute()
            case 'hide_all_encrypted_notes':
                HideAllEncryptedNotes(self.core).execute()
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class EncryptedNoteEntry(DetailEntry):
    def __init__(self, contact_id, note, pos, core, visible=False):
        if visible:
            content = '🔒' + note.content
            super(EncryptedNoteEntry, self).__init__(contact_id, note, content,
                                                     pos, core)
        else:
            super(EncryptedNoteEntry, self).__init__(contact_id, note,
                                                     '🔒(encrypted)', pos, core)
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
                command = f'{EditNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'rename_note':
                command = f'{RenameNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'delete_note':
                command = f'{DeleteNote.name} {self.note.note_id}'
                self.core.ui.console.show_console(command)
            case 'decrypt_note':
                DecryptNote(self.core).execute([self.note.note_id])
            case 'toggle_note_encryption':
                ToggleNoteEncryption(self.core).execute([self.note.note_id])
            case 'show_all_encrypted_notes':
                ShowAllEncryptedNotes(self.core).execute()
            case 'hide_all_encrypted_notes':
                HideAllEncryptedNotes(self.core).execute()
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key


class GoogleNoteEntry(DetailEntry):
    def __init__(self, contact_id, note, pos, core):
        super(GoogleNoteEntry, self).__init__(contact_id, note, note.content,
                                              pos,
                                              core)
        self.note = note


class GoogleAttributeEntry(DetailEntry):
    def __init__(self, contact_id, attribute, pos, core):
        label = 'G: ' + attribute.key + ': ' + attribute.value
        super(GoogleAttributeEntry, self).__init__(contact_id, attribute, label,
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
            case 'copy_attribute':
                pyperclip.copy(self.attribute.value)
                msg = "Copied \"" + self.attribute.value + "\" to clipboard."
                self.core.ui.console.show_message(msg)
            case _:
                self.core.keybindings.set(command_key, command_repeat)
                self.core.keybindings.set_bubbling(True)
                return key
