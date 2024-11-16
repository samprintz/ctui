from ctui.enum.view import View
from ctui.model.attribute import Attribute
from ctui.model.contact import Contact
from ctui.model.encrypted_note import EncryptedNote
from ctui.model.gift import Gift
from ctui.model.note import Note


class Command:
    names = []

    def __init__(self, core):
        self.core = core

    def execute(self, args):
        pass


class AddContact(Command):
    name = 'add-contact'
    names = ['add-contact']

    def execute(self, args):
        name = " ".join(args)
        contact = Contact(name)
        msg = self.core.add_contact(contact)

        # TODO not define this parameters in execute()?
        self.core.ui.update_view(True, True, View.LIST, contact, 0)
        self.core.ui.console.show_message(msg)


class RenameContact(Command):
    name = 'rename-contact'
    names = ['rename-contact']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        new_name = " ".join(args)
        msg = self.core.rename_contact(contact, new_name)
        contact.name = new_name  # to find the position by the name

        # TODO not define this parameters in execute()?
        self.core.ui.update_view(True, False, View.LIST, contact, None)
        self.core.ui.console.show_message(msg)


class DeleteContact(Command):
    name = 'delete-contact'
    names = ['delete-contact']

    def execute(self, args):
        name = " ".join(args)
        msg = self.core.delete_contact_by_name(name)

        # TODO not define this parameters in execute()?
        self.core.ui.update_view(True, True, View.LIST, None, 0)
        self.core.ui.console.show_message(msg)


class AddAttribute(Command):
    name = 'add-attribute'
    names = ['add-attribute']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)

        msg = self.core.rdfstore.add_attribute(contact, attribute)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(attribute)
        self.core.ui.console.show_message(msg)


class EditAttribute(Command):
    name = 'edit-attribute'
    names = ['edit-attribute']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        key = args[0]
        value = " ".join(args[1:])
        new_attr = Attribute(key, value)
        old_attr = self.core.ui.detail_view.get_focused_detail()

        if old_attr.key == "givenName":  # special case: rename
            msg = self.core.rename_contact(contact, new_attr.value)
        else:
            self.core.rdfstore.edit_attribute(contact, old_attr, new_attr)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(new_attr)
        self.core.ui.console.show_message(msg)

        return msg


class DeleteAttribute(Command):
    name = 'delete-attribute'
    names = ['delete-attribute']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        msg = self.core.rdfstore.delete_attribute(contact, attribute)

        self.core.ui.set_contact_details(contact)

        new_detail_pos = 0
        if self.core.contact_handler.has_details(contact):
            # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)
        self.core.ui.console.show_message(msg)


class AddNote(Command):
    name = 'add-note'
    names = ['add-note']

    def execute(self, args):
        # TODO refactor, is very similar to add-gift (create interface for both?)

        contact = self.core.ui.list_view.get_focused_contact()

        note_name = " ".join(args)
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

    def execute(self, args):
        # TODO refactor, is very similar to add-gift (create interface for both?)

        contact = self.core.ui.list_view.get_focused_contact()

        note_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        note = self.core.ui.detail_view.get_focused_detail()

        new_name = " ".join(args)
        msg = contact.rename_note(note, new_name)

        # TODO doesn't work; does date must be Date class?
        note.note_id = new_name  # to find the position by the name

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(note)
        self.core.ui.console.show_message(msg)


class EditNote(Command):
    name = 'edit-note'
    names = ['edit-note']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        note_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        note_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        note_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        note_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        note_name = " ".join(args)
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

    def execute(self, args=None):
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

    def execute(self, args=None):
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        gift = self.core.ui.detail_view.get_focused_detail()

        new_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
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
