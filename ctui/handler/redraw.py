class Redraw:
    def redraw(self):
        pass


class ContactAddedOrEditedRedraw(Redraw):
    def __init__(self, core, contact):
        self.contact = contact
        self.core = core

    def redraw(self):
        self.core.update_contact_list()
        self.core.ui.focus_list_view()

        self.core.ui.focus_contact(self.contact)
        self.core.ui.focus_detail_pos(0)


class ContactDeletedRedraw(Redraw):
    def __init__(self, core):
        self.core = core

    def redraw(self):
        deleted_contact_pos = self.core.ui.list_view.get_focused_contact_pos()

        self.core.update_contact_list()
        self.core.ui.focus_list_view()

        pos = min(deleted_contact_pos, self.core.ui.list_view.get_count() - 1)

        self.core.ui.focus_contact_pos(pos)
        self.core.ui.focus_detail_pos(0)


class DetailAddedOrEditedRedraw(Redraw):
    def __init__(self, core, detail):
        self.detail = detail
        self.core = core

    def redraw(self):
        self.core.ui.focus_detail_view()
        self.core.ui.focus_detail(self.detail)


class DetailDeletedRedraw(Redraw):
    def __init__(self, core, contact):
        self.core = core
        self.contact = contact

    def redraw(self):
        self.core.ui.focus_detail_view()

        old_detail_pos = self.core.ui.detail_view.get_tab_body().get_focus_position()
        new_detail_pos = 0
        if self.core.contact_handler.has_details(self.contact):
            # don't focus details column if contact has no details
            detail_count = self.core.ui.detail_view.get_tab_body().get_count()
            new_detail_pos = min(old_detail_pos, detail_count - 1)
            self.core.ui.focus_detail_view()
        self.core.ui.focus_detail_pos(new_detail_pos)
