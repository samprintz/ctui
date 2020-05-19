from rdflib import *
from rdflib.resource import *
import pudb


GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
GIFTIDEA_REF = URIRef('http://hiea.de/contact#giftIdea')


"""
Store for interaction with the RDF file that contains information about contacts, their attributes and gift ideas.
"""
class RDFStore:
    def __init__(self, path, namespace):
        self.path = path
        self.g = self.load_file(path)
        self.namespace = namespace

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

    def contains_contact(self, contact):
        return self.contains_contact_name(contact.name)

    def contains_contact_name(self, name):
        return (None, GIVEN_NAME_REF, Literal(name)) in self.g

    def get_contact(self, name):
        pass

    def add_contact(self, contact):
        assert not self.contains_contact(contact)
        try:
            self.g.add((BNode(), GIVEN_NAME_REF, Literal(contact.name)))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception #TODO

    def rename_contact(self, contact, new_name):
        assert self.contains_contact(contact)
        assert contact.name != new_name
        assert not self.contains_contact_name(new_name)
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            person = Resource(self.g, s)
            person.set(GIVEN_NAME_REF, Literal(new_name))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception #TODO

    def delete_contact(self, contact):
        assert self.contains_contact(contact)
        try:
            self.g.remove((None, GIVEN_NAME_REF, Literal(contact.name)))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception #TODO

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

    def has_attribute(self, contact, attribute):
        attribute_ref = URIRef(self.namespace + attribute.key)
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            return (s, attribute_ref, Literal(attribute.value)) in self.g
        except StopIteration:
            return False

    def add_attribute(self, contact, attribute):
        try:
            if not self.contains_contact(contact): # in case just notes exist
                self.add_contact(contact)
            attribute_ref = URIRef(self.namespace + attribute.key)
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            self.g.add((s, attribute_ref, Literal(attribute.value)))
            self.save_file(self.path)
            return ["Attribute ", attribute.key, "=", attribute.value, " added."]
        except Exception as e:
            return str(e)


    def edit_attribute(self, contact, old_attr, new_attr):
        if old_attr.value == new_attr.value:
            return ["Attribute unchanged."]
        try:
            attribute_ref = URIRef(self.namespace + new_attr.key)
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            self.g.remove((s, attribute_ref, Literal(old_attr.value)))
            self.save_file(self.path)
            resource = Resource(self.g, s)
            resource.set(attribute_ref, Literal(new_attr.value))
            self.save_file(self.path)
            return [new_attr.key, " changed to ", new_attr.value, "."]
        except Exception as e:
            return str(e)

    def delete_attribute(self, contact, attribute):
        if not self.has_attribute(contact, attribute):
            return ["Error: ", contact.name, " doesn't own attribute ",
                    attribute.key, "=", attribute.value, "."]
        try:
            attribute_ref = URIRef(self.namespace + attribute.key)
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            self.g.remove((s, attribute_ref, Literal(attribute.value)))
            self.save_file(self.path)
            return [attribute.key, "=", attribute.value, " deleted."]
        except Exception as e:
            return str(e)

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

