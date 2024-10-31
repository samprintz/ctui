import re

import yaml


class Gift:

    def __init__(self, name, desc='', permanent=False, gifted=False,
                 occasions=None):
        Gift.validate_name(name)

        self.name = name
        self.desc = desc
        self.permanent = permanent
        self.gifted = gifted
        self.occasions = occasions

    def __eq__(self, other):
        return self.name == other.name \
            and self.desc == other.desc \
            and self.gifted == other.gifted \
            and self.permanent == other.permanent \
            and self.occasions == other.occasions

    def get_id(self):
        return self.name.replace(' ', '_')

    def to_dict(self):
        data = {}

        if self.permanent:
            data['permanent'] = self.permanent

        if self.gifted:
            data['gifted'] = self.gifted

        if self.occasions is not None:
            data['occasions'] = self.occasions

        return data

    def to_dump(self):
        dump = ''

        gift_dict = self.to_dict()
        if gift_dict:
            dump = yaml.dump(gift_dict, default_flow_style=False)

        return dump

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            desc=data.get("desc"),
            permanent=data.get("permanent"),
            gifted=data.get("gifted"),
            occasions=data.get("occasions", [])
        )

    @classmethod
    def from_dump(cls, gift_id, dump):
        data = {}

        if dump:
            data = yaml.safe_load(dump)

        data['name'] = gift_id.replace('_', ' ')

        return Gift.from_dict(data)

    @classmethod
    def validate_name(cls, name):
        if re.search(r'[^a-zA-Z0-9äöüÄÖÜß -]', name):
            raise ValueError(
                "Failed to create Gift: name contains invalid characters. Only alphanumeric characters spaces and hypens are allowed.")
