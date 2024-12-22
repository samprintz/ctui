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

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)


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

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def edit_attribute(command_repeat, size):
            command = f'{EditAttribute.name} {self.attribute.key} {self.attribute.value}'
            self.core.ui.console.show_console(command)

        def delete_attribute(command_repeat, size):
            command = f'{DeleteAttribute.name} {self.attribute.key} {self.attribute.value}'
            self.core.ui.console.show_console(command)

        def copy_attribute(command_repeat, size):
            pyperclip.copy(self.attribute.value)
            msg = "Copied \"" + self.attribute.value + "\" to clipboard."
            self.core.ui.console.show_message(msg)

        return {
            'edit_attribute': edit_attribute,
            'delete_attribute': delete_attribute,
            'copy_attribute': copy_attribute,
        }


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

        key = super(GiftEntry, self).keypress(size, key)
        if key is None:
            return

        command_id, command_key, command_repeat \
            = self.core.keybindings.keypress(key, self.name)

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def rename_gift(command_repeat, size):
            command = f'{RenameGift.name} {self.gift.name}'
            self.core.ui.console.show_console(command)

        def delete_gift(command_repeat, size):
            command = f'{DeleteGift.name} {self.gift.name}'
            self.core.ui.console.show_console(command)

        return {
            'rename_gift': rename_gift,
            'delete_gift': delete_gift,
        }


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

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def edit_note(command_repeat, size):
            command = f'{EditNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def rename_note(command_repeat, size):
            command = f'{RenameNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def delete_note(command_repeat, size):
            command = f'{DeleteNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def encrypt_note(command_repeat, size):
            EncryptNote(self.core).execute([self.note.note_id])

        def toggle_note_encryption(command_repeat, size):
            ToggleNoteEncryption(self.core).execute([self.note.note_id])

        def show_all_encrypted_notes(command_repeat, size):
            ShowAllEncryptedNotes(self.core).execute()

        def hide_all_encrypted_notes(command_repeat, size):
            HideAllEncryptedNotes(self.core).execute()

        return {
            'edit_note': edit_note,
            'rename_note': rename_note,
            'delete_note': delete_note,
            'encrypt_note': encrypt_note,
            'toggle_note_encryption': toggle_note_encryption,
            'show_all_encrypted_notes': show_all_encrypted_notes,
            'hide_all_encrypted_notes': hide_all_encrypted_notes,
        }


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

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def edit_note(command_repeat, size):
            command = f'{EditNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def rename_note(command_repeat, size):
            command = f'{RenameNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def delete_note(command_repeat, size):
            command = f'{DeleteNote.name} {self.note.note_id}'
            self.core.ui.console.show_console(command)

        def decrypt_note(command_repeat, size):
            DecryptNote(self.core).execute([self.note.note_id])

        def toggle_note_encryption(command_repeat, size):
            ToggleNoteEncryption(self.core).execute([self.note.note_id])

        def show_all_encrypted_notes(command_repeat, size):
            ShowAllEncryptedNotes(self.core).execute()

        def hide_all_encrypted_notes(command_repeat, size):
            HideAllEncryptedNotes(self.core).execute()

        return {
            'edit_note': edit_note,
            'rename_note': rename_note,
            'delete_note': delete_note,
            'decrypt_note': decrypt_note,
            'toggle_note_encryption': toggle_note_encryption,
            'show_all_encrypted_notes': show_all_encrypted_notes,
            'hide_all_encrypted_notes': hide_all_encrypted_notes,
        }


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

        if command_id in self.get_command_map():
            return self.execute_command(command_id, command_repeat, size)
        else:
            self.core.keybindings.set(command_key, command_repeat)
            self.core.keybindings.set_bubbling(True)
            return key

    def execute_command(self, command_id, command_repeat, size):
        command = self.get_command_map()[command_id]
        return command(command_repeat, size)

    def get_command_map(self):
        def copy_attribute(command_repeat, size):
            pyperclip.copy(self.attribute.value)
            msg = "Copied \"" + self.attribute.value + "\" to clipboard."
            self.core.ui.console.show_message(msg)

        return {
            'copy_attribute': copy_attribute,
        }
