from rdflib import *
from rdflib.resource import *


GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
GIFTIDEA_REF = URIRef('http://hiea.de/contact#giftIdea')


"""
Store for interaction with the RDF file that contains information about contacts, their attributes and gift ideas.
"""
class RDFStore:
    def __init__(self, path):
        self.path = path
        self.g = self.load_file(path)

    def load_file(self, path):
        g = Graph()
        g.parse(path, format="n3")
        return g

    def save_file(self, path):
        self.g.serialize(format='n3', indent=True, destination=path)

    def get_all_contact_names(self):
        contact_names = []
        for o in self.g.objects(None, GIVEN_NAME_REF):
            contact_names.append(str(o))
        return sorted(contact_names)

    def get_contact(self, name):
        pass

    def add_contact(self, contact):
        pass

    def rename_contact(self, contact, new_name):
        pass

    def delete_contact(self, contact):
        pass

    def get_details(self, contact):
        pass

    # attributes

    def get_attributes(self, contact):
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        except StopIteration:
            return None
        entries = []
        for p,o in self.g.predicate_objects(s):
            predicate = self.get_predicate_name(p)
            if predicate == 'givenName': continue
            if predicate == 'giftIdea': continue
            entries.append([predicate, str(o)])
        if len(entries) == 0: return None
        return sorted(entries)


    def has_attributes(self, contact):
        pass

    def add_attribute(self, contact, attribute):
        pass

    def edit_attribute(self, contact, old_attr, new_attr):
        pass

    def delete_attribute(self, contact, attribute):
        pass

    # gifts

    def get_gifts(self, contact):
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        except StopIteration:
            return None
        entries = []
        for p,o in self.g.predicate_objects(s):
            predicate = self.get_predicate_name(p)
            if predicate == 'giftIdea':
                entries.append(str(o))
        if len(entries) == 0: return None
        return sorted(entries)

    def has_gifts(self, contact):
        s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        return (s, GIFTIDEA_REF, None) in g

    def add_gift(self, contact, gift):
        pass

    def edit_gift(self, contact, gift):
        pass

    def delete_gift(self, contact, gift):
        pass

    def mark_gifted(self, contact, gift):
        pass

    def unmark_gifted(self, contact, gift):
        pass

    # helper

    def get_predicate_name(self, p):
        return p.split('#',1)[1]

