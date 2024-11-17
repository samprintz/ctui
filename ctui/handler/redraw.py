class Redraw:
    def redraw(self):
        pass


class ContactAddedOrEditedRedraw(Redraw):
    def __init__(self, core, contact):
        self.contact = contact
        self.core = core

    def redraw(self):
        self.core.ui.focus_contact_view()
        self.core.ui.focus_contact(self.contact)
        self.core.ui.focus_detail_pos(0)


class ContactDeletedRedraw(Redraw):
    def __init__(self, core, contact):
        self.contact = contact
        self.core = core

    def redraw(self):
        self.core.ui.focus_contact_view()
        self.core.ui.focus_contact(self.contact)
        self.core.ui.focus_detail_pos(0)


class DetailAddedOrEditedRedraw(Redraw):
    def __init__(self, core, detail):
        self.detail = detail
        self.core = core

    def redraw(self):
        self.core.ui.focus_detail_view()
        self.core.ui.focus_detail(self.detail)
