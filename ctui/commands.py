from ctui.objects import Gift, Attribute


class Command:
    names = []

    def __init__(self, core):
        self.core = core

    def execute(self, args):
        pass


class AddGift(Command):
    name = 'add-gift'
    names = ['add-gift']

    def __init__(self, core):
        super().__init__(core)

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        name = " ".join(args)
        gift = Gift(name)
        msg = contact.add_gift(gift)
        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail(gift)
        return msg


class AddAttribute(Command):
    name = 'add-attribute'
    names = ['add-attribute']

    def __init__(self, core):
        super().__init__(core)

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

    def __init__(self, core):
        super().__init__(core)

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

    def __init__(self, core):
        super().__init__(core)

    def execute(self, args):
        contact = self.core.ui.list_view.get_focused_contact()
        key = args[0]
        value = " ".join(args[1:])
        attribute = Attribute(key, value)
        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()
        msg = contact.delete_attribute(attribute)

        new_detail_pos = 0
        if contact.has_details():  # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()

        self.core.ui.set_contact_details(contact)
        self.core.ui.focus_detail_pos(new_detail_pos)
        return msg
