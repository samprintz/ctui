from typing import List, Union

from ctui.model.attribute import Attribute
from ctui.model.contact import Contact
from ctui.model.gift import Gift
from ctui.model.note import Note


class ContactHandler:
    def __init__(self, core):
        self.core = core

    def load_contacts(self) -> List[Contact]:
        """
        @return: list of contacts *without* contact details
        """
        contacts = []
        for c in self.core.rdfstore.get_contact_names():
            contacts.append(Contact(c))
        for c in self.core.textfilestore.get_contact_names():
            # check if contact already in list
            try:
                existing_contact = next(x for x in contacts if c == x.name)
            except StopIteration:
                contacts.append(Contact(c))
        if self.core.googlestore is not None:
            for contact in self.core.googlestore.load_contacts():
                # check if contact already in list
                try:
                    existing_contact = next(
                        x for x in contacts if contact.name == x.name)
                    contacts.remove(existing_contact)
                    contact.merge(existing_contact)
                except StopIteration:
                    pass
                contacts.append(contact)
        contacts.sort(key=lambda x: x.name)
        return contacts

    def load_contact_names(self) -> List[str]:
        contact_names = self.core.rdfstore.get_contact_names() \
                        + self.core.textfilestore.get_contact_names()

        if self.core.googlestore is not None:
            contact_names + self.core.googlestore.load_contact_names()

        return sorted(set(contact_names))

    def has_details(self, contact) -> List[Union[Attribute, Note, Gift]]:
        return self.core.rdfstore.has_attributes(contact) or \
            self.core.textfilestore.has_gifts(contact.get_id()) or \
            self.core.textfilestore.has_notes(contact.get_id())

    def load_details(self, contact: Contact) -> None:
        contact.attributes = self.core.rdfstore.get_attributes(contact)
        contact.gifts = self.core.textfilestore.get_gifts(contact.get_id())
        contact.notes = self.core.textfilestore.get_notes(contact.get_id())
