from ctui.enum.view import View
from ctui.model.attribute import Attribute
from ctui.model.contact import Contact
from ctui.model.gift import Gift


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
        contact = Contact(name, self.core)
        msg = self.core.add_contact(contact)

        # TODO not define this parameters in execute()?
        self.core.ui.update_view(True, True, View.LIST, contact, 0)

        return msg


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

        return msg


class DeleteContact(Command):
    name = 'delete-contact'
    names = ['delete-contact']

    def execute(self, args):
        name = " ".join(args)
        msg = self.core.delete_contact_by_name(name)

        # TODO not define this parameters in execute()?
        self.core.ui.update_view(True, True, View.LIST, None, 0)

        return msg


class AddAttribute(Command):
    name = 'add-attribute'
    names = ['add-attribute']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)
        msg = contact.add_attribute(attribute)

        self.core.ui.set_contact_details(contact)

        self.core.ui.focus_detail(attribute)
        return msg


class EditAttribute(Command):
    name = 'edit-attribute'
    names = ['edit-attribute']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        key = args[0]
        value = " ".join(args[1:])
        new_attr = Attribute(key, value)
        old_attr = self.core.ui.detail_view.get_focused_detail()
        msg = contact.edit_attribute(old_attr, new_attr)

        self.core.ui.set_contact_details(contact)

        self.core.ui.focus_detail(new_attr)

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
        msg = contact.delete_attribute(attribute)

        self.core.ui.set_contact_details(contact)

        new_detail_pos = 0
        if contact.has_details():  # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)

        return msg


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

        return msg


class AddGift(Command):
    name = 'add-gift'
    names = ['add-gift']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        # TODO use random temp path instead?
        path = self.core.textfilestore.prepare_gift_file(contact.get_id())

        content = self.core.editor.edit(path)
        gift = Gift.from_dump(gift_id, content)
        msg = self.core.textfilestore.add_gift(contact.get_id(), gift)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)

        return msg


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

        return msg


class EditGift(Command):
    name = 'edit-gift'
    names = ['edit-gift']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()

        gift_name = " ".join(args)
        Gift.validate_name(gift_name)
        gift_id = Gift.name_to_id(gift_name)

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        # TODO use random temp path instead?
        path = self.core.textfilestore.prepare_gift_file(contact.get_id())

        filepath = self.core.textfilestore.get_gift_filepath(contact.get_id(),
                                                             gift_id)
        with open(filepath) as f:
            content = f.read()

        new_content = self.core.editor.edit(path, content)
        gift = Gift.from_dump(gift_id, new_content)
        msg = self.core.textfilestore.edit_gift(self, contact.get_id(), gift_id,
                                                gift)

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)

        return msg


class DeleteGift(Command):
    name = 'delete-gift'
    names = ['delete-gift']

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()

        gift_name = " ".join(args)
        Gift.validate_name(gift_name)
        gift_id = gift_name.replace(" ", "_")

        if self.core.textfilestore.has_gift(contact.get_id(), gift_id):
            raise ValueError(f'Gift "{gift_id}" does not exist')

        msg = self.core.textfilestore.delete_gift(self, contact.get_id(),
                                                  gift_id)

        self.core.ui.set_contact_details(contact)

        new_detail_pos = 0
        if contact.has_details():  # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)

        return msg


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

        return msg


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

        return msg


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

        return msg


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

        return msg
