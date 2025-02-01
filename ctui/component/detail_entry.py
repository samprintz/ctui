import pyperclip

from ctui.commands import EditAttribute, DeleteAttribute, RenameGift, EditGift, \
    EditNote, RenameNote, DeleteNote, DeleteGift, EncryptNote, DecryptNote, \
    ToggleNoteEncryption, ShowAllEncryptedNotes, HideAllEncryptedNotes
from ctui.keybindings import KeybindingMixin, KeybindingCommand
from ctui.component.list_entry import CListEntry


class DetailEntry(CListEntry, KeybindingMixin):
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
        return self.handle_keypress(size, key)

    @KeybindingCommand("edit_attribute")
    def edit_attribute(self, command_repeat, size):
        command = f'{EditAttribute.name} {self.attribute.key} {self.attribute.value}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("delete_attribute")
    def delete_attribute(self, command_repeat, size):
        command = f'{DeleteAttribute.name} {self.attribute.key} {self.attribute.value}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("copy_attribute")
    def copy_attribute(self, command_repeat, size):
        pyperclip.copy(self.attribute.value)
        msg = "Copied \"" + self.attribute.value + "\" to clipboard."
        self.core.ui.console.show_message(msg)


class GiftEntry(DetailEntry):
    def __init__(self, contact_id, gift, pos, core):
        label = ''

        if gift.gifted and gift.permanent:
            label += '↻🗹 '
        elif gift.gifted and not gift.permanent:
            label += ' 🗹 '
        elif not gift.gifted and gift.permanent:
            label += '↻  '
        elif not gift.gifted and not gift.permanent:
            label += '   '

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

        return self.handle_keypress(size, key)

    @KeybindingCommand("rename_gift")
    def rename_gift(self, command_repeat, size):
        command = f'{RenameGift.name} {self.gift.name}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("delete_gift")
    def delete_gift(self, command_repeat, size):
        command = f'{DeleteGift.name} {self.gift.name}'
        self.core.ui.console.show_console(command)


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

        return self.handle_keypress(size, key)

    @KeybindingCommand("edit_note")
    def edit_note(self, command_repeat, size):
        command = f'{EditNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("rename_note")
    def rename_note(self, command_repeat, size):
        command = f'{RenameNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("delete_note")
    def delete_note(self, command_repeat, size):
        command = f'{DeleteNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("encrypt_note")
    def encrypt_note(self, command_repeat, size):
        EncryptNote(self.core).execute([self.note.note_id])

    @KeybindingCommand("toggle_note_encryption")
    def toggle_note_encryption(self, command_repeat, size):
        ToggleNoteEncryption(self.core).execute([self.note.note_id])

    @KeybindingCommand("show_all_encrypted_notes")
    def show_all_encrypted_notes(self, command_repeat, size):
        ShowAllEncryptedNotes(self.core).execute()

    @KeybindingCommand("hide_all_encrypted_notes")
    def hide_all_encrypted_notes(self, command_repeat, size):
        HideAllEncryptedNotes(self.core).execute()


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
        return self.handle_keypress(size, key)

    @KeybindingCommand("edit_note")
    def edit_note(self, command_repeat, size):
        command = f'{EditNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("rename_note")
    def rename_note(self, command_repeat, size):
        command = f'{RenameNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("delete_note")
    def delete_note(self, command_repeat, size):
        command = f'{DeleteNote.name} {self.note.note_id}'
        self.core.ui.console.show_console(command)

    @KeybindingCommand("decrypt_note")
    def decrypt_note(self, command_repeat, size):
        DecryptNote(self.core).execute([self.note.note_id])

    @KeybindingCommand("toggle_note_encryption")
    def toggle_note_encryption(self, command_repeat, size):
        ToggleNoteEncryption(self.core).execute([self.note.note_id])

    @KeybindingCommand("show_all_encrypted_notes")
    def show_all_encrypted_notes(self, command_repeat, size):
        ShowAllEncryptedNotes(self.core).execute()

    @KeybindingCommand("hide_all_encrypted_notes")
    def hide_all_encrypted_notes(self, command_repeat, size):
        HideAllEncryptedNotes(self.core).execute()


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
        return self.handle_keypress(size, key)

    @KeybindingCommand("copy_attribute")
    def copy_attribute(self, command_repeat, size):
        pyperclip.copy(self.attribute.value)
        msg = "Copied \"" + self.attribute.value + "\" to clipboard."
        self.core.ui.console.show_message(msg)
