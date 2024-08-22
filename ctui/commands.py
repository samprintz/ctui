from ctui.objects import Gift


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
