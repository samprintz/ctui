from rdflib import *
from rdflib.resource import *

from ctui.model.contact import Contact

GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
GIFTIDEA_REF = URIRef('http://hiea.de/contact#giftIdea')


class RDFStore:
    """
    Store for interaction with the RDF file that contains information about contacts, their attributes and gift ideas.
    """

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

    def get_contact_names(self):
        contact_names = []
        for o in self.g.objects(None, GIVEN_NAME_REF):
            contact_names.append(str(o))
        return sorted(contact_names)

    def contains_contact(self, contact_id):
        has_contact = False

        if contact_id:
            name = Contact.id_to_name(contact_id)
            has_contact = (None, GIVEN_NAME_REF, Literal(name)) in self.g

        return has_contact

    def contains_attribute(self, attr):
        attribute_ref = URIRef(self.namespace + attr.key)
        return (None, attribute_ref, Literal(attr.value)) in self.g

    def get_contact(self, name):
        pass

    def add_contact(self, contact):
        assert not self.contains_contact(contact)

        try:
            self.g.add((BNode(), GIVEN_NAME_REF, Literal(contact.name)))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception  # TODO

    def rename_contact(self, contact, new_name):
        assert self.contains_contact(contact)
        assert contact.name != new_name
        assert not self.contains_contact(Contact.name_to_id(new_name))

        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            person = Resource(self.g, s)
            person.set(GIVEN_NAME_REF, Literal(new_name))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception  # TODO

    def delete_contact(self, contact_id):
        assert self.contains_contact(contact_id)

        try:
            name = Contact.id_to_name(contact_id)
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(name)))
            self.g.remove((s, None, None))
            self.save_file(self.path)
            return True
        except Exception:
            raise Exception  # TODO

    def get_details(self, contact):
        pass

    # attributes

    def has_attributes(self, contact):
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        except StopIteration:
            return False
        triples = [po for po in self.g.predicate_objects(s)]
        return len(triples) > 1

    def get_attributes(self, contact_id):
        attributes = []

        if contact_id:
            name = Contact.id_to_name(contact_id)
            try:
                s = next(self.g.subjects(GIVEN_NAME_REF, Literal(name)))
            except StopIteration:
                return attributes

            for p, o in self.g.predicate_objects(s):
                predicate = self.get_predicate_name(p)
                if predicate == 'givenName': continue
                if predicate == 'giftIdea': continue
                attributes.append([predicate, str(o)])

        return sorted(attributes)

    def has_attribute(self, contact, attribute):
        attribute_ref = URIRef(self.namespace + attribute.key)
        try:
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            return (s, attribute_ref, Literal(attribute.value)) in self.g
        except StopIteration:
            return False

    def add_attribute(self, contact, attribute):
        if not self.contains_contact(contact):  # in case just notes exist
            self.add_contact(contact)

        try:
            attribute_ref = URIRef(self.namespace + attribute.key)
            s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
            self.g.add((s, attribute_ref, Literal(attribute.value)))
            self.save_file(self.path)
            return "Attribute {}={} added.".format(attribute.key,
                                                   attribute.value)
        except Exception as e:
            raise e  # TODO

    def edit_attribute(self, contact, old_attr, new_attr):
        if not self.has_attribute(contact, old_attr):
            raise ValueError(
                f'"{contact.get_id()}" doesn\'t own attribute {old_attr.key}={old_attr.value}')

        if old_attr.key == new_attr.key and old_attr.value == new_attr.value:
            return "Warning: Attribute unchanged."

        old_attr_ref = URIRef(self.namespace + old_attr.key)
        s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        self.g.remove((s, old_attr_ref, Literal(old_attr.value)))
        self.save_file(self.path)
        new_attr_ref = URIRef(self.namespace + new_attr.key)
        self.g.add((s, new_attr_ref, Literal(new_attr.value)))
        self.save_file(self.path)
        return f'{new_attr.key} changed to {new_attr.value}'

    def delete_attribute(self, contact, attribute):
        if not self.has_attribute(contact, attribute):
            raise ValueError(
                f'{contact.name} doesn\'t own attribute {attribute.key}={attribute.value}')

        attribute_ref = URIRef(self.namespace + attribute.key)
        s = next(self.g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        self.g.remove((s, attribute_ref, Literal(attribute.value)))
        self.save_file(self.path)
        return "{}={} deleted".format(attribute.key, attribute.value)

    # helper

    def get_predicate_name(self, p):
        return p.split('#', 1)[1]
