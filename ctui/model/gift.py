import re

import yaml

from ctui import util


class Gift:

    def __init__(self, name, desc='', permanent=False, gifted=False,
                 occasions=None):
        Gift.validate_name(name)

        self.name = name
        self.desc = desc
        self.permanent = permanent
        self.gifted = gifted
        self.occasions = occasions

    def __str__(self):
        return f'Gift({self.name})'

    def __repr__(self):
        return f'Gift({self.name}, gifted={self.gifted}, permanent={self.permanent},occasions={len(self.occasions)})'

    def __eq__(self, other):
        return self.name == other.name \
            and self.desc == other.desc \
            and self.gifted == other.gifted \
            and self.permanent == other.permanent \
            and self.occasions == other.occasions

    def get_id(self):
        return Gift.name_to_id(self.name)

    def to_dict(self):
        data = {}

        if self.desc:
            data['desc'] = self.desc

        if self.permanent:
            data['permanent'] = self.permanent

        if self.gifted:
            data['gifted'] = self.gifted

        if self.occasions is not None and len(self.occasions) > 0:
            data['occasions'] = self.occasions

        return data

    def to_dump(self):
        dump = ''

        gift_dict = self.to_dict()
        if gift_dict:
            dump = yaml.dump(gift_dict,
                             default_flow_style=False,
                             allow_unicode=True)

        return dump.strip()

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            desc=data.get("desc"),
            permanent=data.get("permanent", False),
            gifted=data.get("gifted", False),
            occasions=data.get("occasions", [])
        )

    @classmethod
    def from_dump(cls, gift_id, dump):
        data = {}

        if dump:
            data = yaml.safe_load(dump)

        if not isinstance(data, dict):
            raise ValueError(f'Invalid gift file content "{gift_id}"')

        data['name'] = Gift.id_to_name(gift_id)

        return Gift.from_dict(data)

    @classmethod
    def validate_name(cls, name: str) -> None:
        if re.search(util.alphanumeric, name):
            raise ValueError(
                f"Invalid gift name '{name}': contains invalid characters. Only alphanumeric characters spaces and hypens are allowed.")

    @classmethod
    def name_to_id(cls, name):
        return name.replace(' ', '_')

    @classmethod
    def id_to_name(cls, gift_id):
        return gift_id.replace('_', ' ')

    @classmethod
    def id_to_filename(cls, gift_id):
        return f'{gift_id}.yaml'
