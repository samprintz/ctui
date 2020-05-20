import core


class Contact:

    def __init__(self, name, core, attributes=None, gifts=None, notes=None):
        self.name = name
        self.core = core
        self.attributes = attributes
        self.gifts = gifts
        self.notes = notes

    def get_details(self):
        self.attributes = self.get_attributes()
        self.gifts = self.get_gifts()
        self.notes = self.get_notes()

    # attributes

    def get_attributes(self):
        return self.core.rdfstore.get_attributes(self)

    def add_attribute(self, attribute):
        return self.core.rdfstore.add_attribute(self, attribute)

    def edit_attribute(self, old_attr, new_attr):
        return self.core.rdfstore.edit_attribute(self, old_attr, new_attr)

    def delete_attribute(self, attribute):
        return self.core.rdfstore.delete_attribute(self, attribute)

    # gifts

    def get_gifts(self):
        return self.core.rdfstore.get_gifts(self)

    def add_gift(self, gift):
        return self.core.rdfstore.add_gift(self, gift)

    def edit_gift(self, old_gift, new_gift):
        return self.core.rdfstore.edit_gift(self, old_gift, new_gift)

    def delete_gift(self, gift):
        return self.core.rdfstore.delete_gift(self, gift)

    # notes

    def get_notes(self):
        return self.core.notesstore.get_notes(self)

    def add_note(self, date_str):
        return self.core.notesstore.add_note(self, date_str)

    def edit_note(self, date_str):
        return self.core.notesstore.edit_note(self, date_str)

    def delete_note(self, date_str):
        return self.core.notesstore.delete_note(self, date_str)


class Attribute:

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Gift:

    def __init__(self, name):
        self.name = name


class Note:

    def __init__(self, date, content):
        self.date = date
        self.content = content

