from ctui.model.contact import Contact


class GoogleContact(Contact):

    def __init__(self, name, core, google_id, google_attributes=None,
                 google_notes=None):
        super(GoogleContact, self).__init__(name, core)
        self.google_id = google_id
        self.google_attributes = google_attributes
        self.google_notes = google_notes

    def merge(self, contact):
        self.attributes = contact.attributes
        self.gifts = contact.gifts
        self.notes = contact.notes
        return self
