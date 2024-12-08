import re
from typing import List

from ctui.model.attribute import Attribute
from ctui.model.gift import Gift
from ctui.model.note import Note


class Contact:

    def __init__(self,
                 name: str,
                 attributes: List[Attribute] = None,
                 gifts: List[Gift] = None,
                 notes: List[Note] = None
                 ):
        self.name = name
        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_id(self) -> str:
        return Contact.name_to_id(self.name)

    def __str__(self):
        return f'Contact({self.name})'

    @classmethod
    def validate_name(cls, name: str) -> None:
        if re.search(r'[^a-zA-Z0-9äöüÄÖÜß -]', name):
            raise ValueError(
                f"Invalid contact name '{name}': contains invalid characters. Only alphanumeric characters spaces and hypens are allowed.")

    @classmethod
    def id_to_name(cls, contact_id: str) -> str:
        return contact_id.replace('_', ' ')

    @classmethod
    def name_to_id(cls, name: str) -> str:
        Contact.validate_name(name)
        return name.replace(' ', '_')
