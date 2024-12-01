from ctui.handler.redraw import \
    ContactDeletedRedraw, \
    DetailDeletedRedraw, \
    DetailAddedOrEditedRedraw, \
    ContactAddedOrEditedRedraw
from ctui.model.attribute import Attribute
from ctui.model.contact import Contact
from ctui.model.encrypted_note import EncryptedNote
from ctui.model.gift import Gift
from ctui.model.note import Note


class Command:
    names = []

    def __init__(self, core):
        self.core = core

        self.input = ""

        self.focused_contact = None
        self.focused_detail = None

        self.to_focus_contact = None
        self.to_focus_detail = None

        self.msg = ""

    def execute(self, args):
        self.focused_contact = self.core.ui.list_view.get_focused_contact()
        self.focused_detail = self.core.ui.detail_view.get_focused_detail()

        arg = " ".join(args)
        if self._is_custom_input_handling():
            arg = args

        self._execute(arg)
        self._update()
        self.core.ui.console.show_message(self.msg)

    def _is_custom_input_handling(self):
        return False

    def _execute(self, args):
        raise NotImplementedError()

    def _update(self):
        pass


class AddContact(Command):
    name = 'add-contact'
    names = ['add-contact']

    def _execute(self, name):
        contact = Contact(name)
        self.msg = self.core.add_contact(contact)
        self.to_focus_contact = contact

    def _update(self):
        ContactAddedOrEditedRedraw(self.core, self.to_focus_contact).redraw()


class RenameContact(Command):
    name = 'rename-contact'
    names = ['rename-contact']

    def _execute(self, new_name):
        self.msg = self.core.rename_contact(self.focused_contact, new_name)
        self.to_focus_contact = Contact(new_name)

    def _update(self):
        ContactAddedOrEditedRedraw(self.core, self.to_focus_contact).redraw()


class DeleteContact(Command):
    name = 'delete-contact'
    names = ['delete-contact']

    def _execute(self, name):
        self.msg = self.core.delete_contact_by_name(name)

    def _update(self):
        ContactDeletedRedraw(self.core).redraw()


class AddAttribute(Command):
    name = 'add-attribute'
    names = ['add-attribute']

    def _is_custom_input_handling(self):
        return True

    def _execute(self, args):
        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)
        self.to_focus_detail = attribute
        self.msg = self.core.rdfstore.add_attribute(self.focused_contact,
                                                    attribute)

    def _update(self):
        DetailAddedOrEditedRedraw(self.core, self.to_focus_detail).redraw()


class EditAttribute(Command):
    name = 'edit-attribute'
    names = ['edit-attribute']

    def _is_custom_input_handling(self):
        return True

    def _execute(self, args):
        key = args[0]
        value = " ".join(args[1:])
        new_attr = Attribute(key, value)
        old_attr = self.core.ui.detail_view.get_focused_detail()
        self.to_focus_detail = new_attr

        if old_attr.key == "givenName":  # special case: rename
            self.msg = self.core.rename_contact(self.focused_contact,
                                                new_attr.value)
        else:
            self.msg = self.core.rdfstore.edit_attribute(self.focused_contact,
                                                         old_attr, new_attr)

    def _update(self):
        DetailAddedOrEditedRedraw(self.core, self.to_focus_detail).redraw()


class DeleteAttribute(Command):
    name = 'delete-attribute'
    names = ['delete-attribute']

    def _is_custom_input_handling(self):
        return True

    def _execute(self, args):
        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)
        self.msg = self.core.rdfstore.delete_attribute(self.focused_contact,
                                                       attribute)

    def _update(self):
        DetailDeletedRedraw(self, self.focused_contact)


class AddNote(Command):
    name = 'add-note'
    names = ['add-note']

    def _execute(self, note_name):
        # TODO refactor, is very similar to add-gift (create interface for both?)

        contact = self.core.ui.list_view.get_focused_contact()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" does already exist')

        # TODO use random temp path instead?
        self.core.textfilestore.create_note_dir(contact.get_id())
        filepath = self.core.textfilestore.get_note_filepath(contact.get_id(),
                                                             note_id)

        content = self.core.editor.add(filepath)
        note = Note.from_dump(note_id, content)
        msg = self.core.textfilestore.add_note(contact.get_id(), note)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(note)
        self.core.ui.console.show_message(msg)


class AddEncryptedNote(Command):
    name = 'add-encrypted-note'
    names = ['add-encrypted-note']

    def _execute(self, note_name):
        # TODO refactor, is very similar to add-gift (create interface for both?)

        contact = self.core.ui.list_view.get_focused_contact()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if self.core.textfilestore.has_gift(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" does already exist')

        # TODO use random temp path instead?
        self.core.textfilestore.create_note_dir(contact.get_id())
        filepath = self.core.textfilestore.get_note_filepath(contact.get_id(),
                                                             note_id)

        content = self.core.editor.add(filepath)
        note = EncryptedNote.from_dump(note_id, content)
        msg = self.core.textfilestore.add_encrypted_note(contact.get_id(), note)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(note)
        self.core.ui.console.show_message(msg)


class RenameNote(Command):
    name = 'rename-note'
    names = ['rename-note']

    def _execute(self, new_name):
        contact = self.core.ui.list_view.get_focused_contact()
        note = self.core.ui.detail_view.get_focused_detail()

        msg = contact.rename_note(note, new_name)

        # TODO doesn't work; does date must be Date class?
        note.note_id = new_name  # to find the position by the name

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(note)
        self.core.ui.console.show_message(msg)


class EditNote(Command):
    name = 'edit-note'
    names = ['edit-note']

    def _execute(self, note_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if not self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        filepath = self.core.textfilestore.get_note_filepath(contact.get_id(),
                                                             note_id)

        # TODO use random temp path instead?
        self.core.textfilestore.create_note_dir(contact.get_id())

        new_content = self.core.editor.edit(filepath)
        note = Note.from_dump(note_id, new_content)
        msg = self.core.textfilestore.edit_note(contact.get_id(), note_id, note)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(note)
        self.core.ui.console.show_message(msg)


class DeleteNote(Command):
    name = 'delete-note'
    names = ['delete-note']

    def _execute(self, note_name):
        contact = self.core.ui.list_view.get_focused_contact()
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if not self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        msg = self.core.textfilestore.delete_note(contact.get_id(), note_id)

        self.core.ui.set_contact_details(contact)

        new_detail_pos = 0
        if self.core.contact_handler.has_details(contact):
            # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)
        self.core.ui.console.show_message(msg)


class EncryptNote(Command):
    name = 'encrypt-note'
    names = ['encrypt-note']

    def _execute(self, note_name):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if not self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        msg = self.core.textfilestore.encrypt_note(contact.get_id(), note_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(detail_pos)
        self.core.ui.console.show_message(msg)


class DecryptNote(Command):
    name = 'decrypt-note'
    names = ['decrypt-note']

    def _execute(self, note_name):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if not self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        msg = self.core.textfilestore.decrypt_note(contact.get_id(), note_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(detail_pos)
        self.core.ui.console.show_message(msg)


class ToggleNoteEncryption(Command):
    name = 'toggle-note-encryption'
    names = ['toggle-note-encryption']

    def _execute(self, note_name):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        Note.validate_name(note_name)
        note_id = Note.name_to_id(note_name)

        if not self.core.textfilestore.has_note(contact.get_id(), note_id):
            raise ValueError(f'Note "{note_id}" doesn\'t exist')

        if self.core.memorystore.has_note(contact.get_id(), note_id):  # hide
            self.core.memorystore.delete_note(contact.get_id(), note_id)
            msg = "Hide encrypted note content"
        else:  # show
            content = self.core.textfilestore.get_encrypted_note_text(
                contact.get_id(),
                note_id)
            encrypted_note = EncryptedNote(note_id, content)
            if self.core.memorystore.add_note(contact.get_id(), encrypted_note):
                msg = "Show encrypted note content"
            else:
                raise Exception("Failed to show encrypted note content")

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(detail_pos)
        self.core.ui.console.show_message(msg)


class ShowAllEncryptedNotes(Command):
    name = 'show-all-encrypted-notes'
    names = ['show-all-encrypted-notes']

    def _execute(self, args=None):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        if not self.core.textfilestore.has_encrypted_notes(contact.get_id()):
            raise Exception("No encrypted notes found")

        for note in self.core.textfilestore.get_encrypted_notes(
                contact.get_id()):
            content = self.core.textfilestore.get_encrypted_note_text(
                contact.get_id(),
                note.note_id)
            note = EncryptedNote(note.note_id, content)
            self.core.memorystore.add_note(contact.get_id(), note)

        msg = "Show content of all encrypted notes"

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(detail_pos)
        self.core.ui.console.show_message(msg)


class HideAllEncryptedNotes(Command):
    name = 'hide-all-encrypted-notes'
    names = ['hide-all-encrypted-notes']

    def _execute(self, args=None):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        if not self.core.memorystore.has_notes(contact.get_id()):
            raise Exception("All encrypted notes are hidden")

        self.core.memorystore.delete_all_notes(contact.get_id())
        msg = "Hide content of all encrypted notes"

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(detail_pos)
        self.core.ui.console.show_message(msg)


class AddGift(Command):
    name = 'add-gift'
    names = ['add-gift']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = Gift.name_to_id(gift_name)

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_name}" does already exist')

        # TODO use random temp path instead?
        self.core.textfilestore.create_gift_dir(contact.get_id())
        filepath = self.core.textfilestore.get_gift_filepath(contact.get_id(),
                                                             gift_id)

        content = self.core.editor.add(filepath)
        gift = Gift.from_dump(gift_id, content)
        msg = self.core.textfilestore.add_gift(contact.get_id(), gift)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class RenameGift(Command):
    name = 'rename-gift'
    names = ['rename-gift']

    def _execute(self, new_name):
        contact = self.core.ui.list_view.get_focused_contact()
        gift = self.core.ui.detail_view.get_focused_detail()

        Gift.validate_name(new_name)

        if gift.name == new_name:
            return "Warning: Name unchanged"

        if self.core.textfilestore.has_gift(Gift.name_to_id(new_name)):
            raise ValueError(f'Gift {new_name} already exists')

        msg = self.core.textfilestore.rename_gift(contact.get_id(),
                                                  gift.get_id(),
                                                  new_name)

        gift.name = new_name  # to focus the renamed detail

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class EditGift(Command):
    name = 'edit-gift'
    names = ['edit-gift']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = Gift.name_to_id(gift_name)

        if not self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" doesn\'t exist')

        filepath = self.core.textfilestore.get_gift_filepath(contact.get_id(),
                                                             gift_id)

        # TODO use random temp path instead?
        self.core.textfilestore.create_gift_dir(contact.get_id())

        new_content = self.core.editor.edit(filepath)
        gift = Gift.from_dump(gift_id, new_content)
        msg = self.core.textfilestore.edit_gift(contact.get_id(), gift_id, gift)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class DeleteGift(Command):
    name = 'delete-gift'
    names = ['delete-gift']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        Gift.validate_name(gift_name)
        gift_id = Gift.name_to_id(gift_name)

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" doesn\'t exist')

        msg = self.core.textfilestore.delete_gift(self, contact.get_id(),
                                                  gift_id)

        self.core.ui.set_contact_details(contact)

        new_detail_pos = 0
        if self.core.contact_handler.has_details(contact):
            # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)
        self.core.ui.console.show_message(msg)


class MarkGifted(Command):
    name = 'mark-gifted'
    names = ['mark-gifted']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        msg = self.core.textfilestore.mark_gifted(self, contact.get_id(),
                                                  gift_id)

        gift = self.core.textfilestore.get_gift(self, contact.get_id(), gift_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class UnmarkGifted(Command):
    name = 'unmark-gifted'
    names = ['unmark-gifted']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        msg = self.core.textfilestore.unmark_gifted(self, contact.get_id(),
                                                    gift_id)

        gift = self.core.textfilestore.get_gift(self, contact.get_id(), gift_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class MarkPermanent(Command):
    name = 'mark-permanent'
    names = ['mark-permanent']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        msg = self.core.textfilestore.mark_permanent(self, contact.get_id(),
                                                     gift_id)

        gift = self.core.textfilestore.get_gift(self, contact.get_id(), gift_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)


class UnmarkPermanent(Command):
    name = 'unmark-permanent'
    names = ['unmark-permanent']

    def _execute(self, gift_name):
        contact = self.core.ui.list_view.get_focused_contact()

        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        msg = self.core.textfilestore.unmark_permanent(self, contact.get_id(),
                                                       gift_id)

        gift = self.core.textfilestore.get_gift(self, contact.get_id(), gift_id)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        self.core.ui.console.show_message(msg)
