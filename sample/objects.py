from core import *


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


    def has_attributes(self):
        return self.core.rdfstore.has_attributes(self)


    def has_attribute(self, attribute):
        return self.core.rdfstore.has_attribute(self, attribute)


    def add_attribute(self, attribute):
        return self.core.rdfstore.add_attribute(self, attribute)


    def edit_attribute(self, old_attr, new_attr):
        if old_attr.key == "givenName": # special case: rename
            return self.core.rename_contact(self, new_attr.value)

        if not self.has_attribute(old_attr):
            return "Error: {} doesn't own attribute {}={}.".format(
                    self.name, old_attr.key, old_attr.value)

        if old_attr.value == new_attr.value:
            return "Warning: Attribute unchanged."

        return self.core.rdfstore.edit_attribute(self, old_attr, new_attr)


    def delete_attribute(self, attribute):
        if not self.has_attribute(attribute):
            return "Error: {} doesn't own attribute {}={}.".format(
                    self.name, old_attr.key, old_attr.value)

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

    def has_notes(self):
        return self.core.notesstore.has_notes(self)


    def get_notes(self):
        return self.core.notesstore.get_notes(self)


    def get_notes_path(self):
        return self.core.notesstore.get_notes_path(self)


    def has_note(self, date):
        return self.core.notesstore.contains_note(self, date)


    def get_note(self, date):
        if not self.has_note(date):
            return "Error: Note doesn't exist."
        return self.core.notesstore.get_note(self, date)


    def add_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if self.has_note(date):
            return self.edit_note(date_str)

        try:
            content = self.core.editor.add(self.get_notes_path(), date_str)
        except OSError:
            return "Error: Note couldn't be added."

        return self.core.notesstore.add_note(self, date, content)


    def rename_note(self, note, date_str):
        try:
            new_date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "Error: \"{}\" not in format YYYYMMDD.".format(date_str)

        if note.date == new_date:
            return "Warning: Name unchanged."

        if self.has_note(new_date):
            return "Error: Note {} already exists.".format(date_str)

        return self.core.notesstore.rename_note(self, note, new_date)


    def delete_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.has_note(date):
            return "Error: No note for \"{}\".".format(date_str)

        return self.core.notesstore.delete_note(self, date)


    def edit_note(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            return "\"{}\" not in format YYYYMMDD.".format(date_str)

        if not self.has_note(date):
            return self.add_note(self, date_str)

        try:
            new_content = self.core.editor.edit(self.get_notes_path(), date_str)
        except OSError:
            return "Error: Note couldn't be edited."

        return self.core.notesstore.edit_note(self, date, new_content)



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

