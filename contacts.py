from rdflib import *
from rdflib.resource import *
from datetime import date,datetime
from subprocess import call
import operator
import os
import pudb
import pyperclip
import shutil
import urwid

RUN_DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
CONTACTS_FILE = 'test.n3'
NOTES_DIR = 'Menschen/'
CONTACTS_PATH = RUN_DIR + CONTACTS_FILE
NOTES_PATH = RUN_DIR + NOTES_DIR

EDITOR = os.environ.get('EDITOR','vim')

NAMESPACE = 'http://hiea.de/contact#'
GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
GIFTIDEA_REF = URIRef('http://hiea.de/contact#giftIdea')

NAV_WIDTH = 24
DETAILS_WIDTH = 48

palette = [
    (None,  'light gray', 'black'),
    ('options', 'light gray', 'black'),
    ('focus options', 'black', 'light gray'),
    ('selected', 'black', 'light gray'),
    ('status_bar', 'light gray', 'black')]

focus_map = {
    'options': 'focus options'}


### N3 functions

def load_file(path):
    g = Graph()
    g.parse(path, format="n3")
    return g

def save_file(path):
    g.serialize(format='n3', indent=True, destination=path)

def contains_contact(name):
    return (None, GIVEN_NAME_REF, Literal(name)) in g

def contains_attribute(name, key, value):
    attribute_ref = URIRef(NAMESPACE + key)
    s = next(g.subjects(GIVEN_NAME_REF, Literal(name)))
    return (s, attribute_ref, Literal(value)) in g

def get_contact_list():
    contacts = get_contact_list_n3() + get_contact_list_of_notes()
    return sorted(set(contacts))

def get_contact_list_n3():
    contacts = []
    for o in g.objects(None, GIVEN_NAME_REF):
        contacts.append(str(o))
    return sorted(contacts)

def get_contact_list_of_notes():
    contacts = []
    for dirname in os.listdir(NOTES_PATH):
        if dirname.endswith('.txt'): continue
        contacts.append(dirname.replace('_', ' '))
    return sorted(contacts)

def get_contact_info(contact):
    details = []
    s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
    for p,o in g.predicate_objects(s):
        p_string = p.split('#',1)[1]
        if p_string == 'givenName': continue
        if p_string == 'giftIdea': continue
        #details.append(p_string + ': ' + str(o))
        details.append([p_string, str(o)])
    return sorted(details)

def has_gifts(contact):
    s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
    return (s, GIFTIDEA_REF, None) in g

def get_contact_gifts(contact):
    details = []
    s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
    for p,o in g.predicate_objects(s):
        p_string = p.split('#',1)[1]
        if p_string == 'giftIdea':
            details.append(str(o))
    return sorted(details)

def has_notes_directory(contact):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    return os.path.isdir(dirname)

def has_notes(contact):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    return os.path.isdir(dirname) and len(os.listdir(dirname)) > 0

def get_contact_notes(contact):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    notes = dict()
    for filename in os.listdir(dirname):
        date = filename.replace('.txt', '')
        content = open(dirname + '/' + filename, "r").read()
        notes[date] = content.strip()
    return notes



# "backend" functions / operations

def rename_contact(contact, old_name, new_name):
    # rename notes directory
    if has_notes_directory(contact):
        dirname = NOTES_PATH + contact.name.replace(' ', '_')
        new_dirname = NOTES_PATH + new_name.replace(' ', '_')
        os.rename(dirname, new_dirname)
    # update N3
    if old_name == new_name:
        return ["Name unchanged."]
    if contains_contact(new_name):
        return ["Error: ", new_name, " already exists."]
    else:
        if contains_contact(old_name):
            triples = [s for s in g.subjects(GIVEN_NAME_REF, Literal(old_name))]
            if len(triples) > 1:
                return ["Error: Multiple persons with name ", old_name, " exist."]
            # update n3
            person = Resource(g, triples[0])
            person.set(GIVEN_NAME_REF, Literal(new_name))
            save_file(CONTACTS_PATH)
            # reload urwid
            fill.body.contents[0][0].base_widget.load_contacts(new_name)
            return [old_name, " renamed to ", new_name, "."]
        else:
            return ["Error: ", old_name, " doesn't exists."]


def add_contact(name):
    if contains_contact(name):
        return ["Error: ", name, " already exists."]
    else:
        # update n3
        g.add( (BNode(), GIVEN_NAME_REF, Literal(name)) )
        save_file(CONTACTS_PATH)
        # reload urwid
        fill.body.contents[0][0].base_widget.load_contacts()
        return [name, " added."]


def delete_contact(contact):
    exists = False
    if contains_contact(contact.name):
        g.remove( (None, GIVEN_NAME_REF, Literal(contact.name)) )
        save_file(CONTACTS_PATH)
        exists = True
    if has_notes_directory(contact):
        dirname = NOTES_PATH + contact.name.replace(' ', '_')
        shutil.rmtree(dirname, ignore_errors=False)
        exists = True
    if exists:
        fill.body.contents[0][0].base_widget.load_contacts()
        return [contact.name, " deleted."]
    else:
        return ["Error: ", contact.name, " doesn't exists."]

def search_contact(name):
    fill.body.contents[0][0].base_widget.jump_to_contact(name)
    return ""


def add_attribute(contact, key, value):
    if not contains_contact(contact.name): # in case just notes exist
        add_contact(contact.name)
    attribute_ref = URIRef(NAMESPACE + key)
    s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
    # update n3
    g.add((s, attribute_ref, Literal(value)))
    save_file(CONTACTS_PATH)
    # reload urwid
    fill.body.contents[0][0].base_widget.load_contacts()
    return ["Attribute ", key, "=", value, " added."]

def edit_attribute(contact, attribute, old_value, new_value):
    if old_value == new_value:
        return ["Attribute unchanged."]
    else:
        attribute_ref = URIRef(NAMESPACE + attribute.key)
        s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        # update n3
        g.remove((s, attribute_ref, Literal(old_value)))
        save_file(CONTACTS_PATH)
        resource = Resource(g, s)
        resource.set(attribute_ref, Literal(new_value))
        save_file(CONTACTS_PATH)
        # reload urwid
        fill.body.contents[0][0].base_widget.load_contacts(contact.name, True)
        return [attribute.key, " changed to ", new_value, "."]

#def set_gift_given(contact, gift):
#    new_value = "x " + gift.value
#    edit_attribute(contact, gift, gift.value, new_value)
#    return ""

def delete_attribute(contact, attribute, key, value):
    if contains_attribute(contact.name, key, value):
        attribute_ref = URIRef(NAMESPACE + key)
        s = next(g.subjects(GIVEN_NAME_REF, Literal(contact.name)))
        # update n3
        g.remove((s, attribute_ref, Literal(value)))
        save_file(CONTACTS_PATH)
        # update urwid
        fill.body.contents[0][0].base_widget.load_contacts()
        return [key, "=", value, " deleted."]
    else:
        return ["Error: ", contact.name, " doesn't own attribute ", key, "=", value, "."]

def add_note(contact, attribute, date):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    if not has_notes_directory(contact):
        os.makedirs(dirname)
    filename = datetime.strftime(date, "%Y%m%d") + ".txt"
    path = dirname + '/' + filename
    try:
        call([EDITOR, path])
        fill.body.contents[0][0].base_widget.load_contacts()
        return "Note added."
    except OSError:
        return "Error: Note not created."

def edit_note(contact, attribute, date):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    filename = datetime.strftime(date, "%Y%m%d") + ".txt"
    path = dirname + '/' + filename
    try:
        call([EDITOR, path])
        fill.body.contents[0][0].base_widget.load_contacts()
        return "Note edited."
    except OSError:
        return "Error: Note can't be edited."

def delete_note(contact, attribute, date):
    dirname = NOTES_PATH + contact.name.replace(' ', '_')
    filename = datetime.strftime(date, "%Y%m%d") + ".txt"
    path = dirname + '/' + filename
    try:
        os.remove(path)
        fill.body.contents[0][0].base_widget.load_contacts()
        return "Note deleted."
    except OSError:
        return "Error: Note can't be deleted."




# urwid functions

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def reload_contact_list(focused_contact=None, focused_attr=None):
    fill.reload_contact_list(focused_contact, focused_attr)

def show_contact_details(contact):
    fill.show_contact_details(contact)

def show_attributes_meta(note):
    date = datetime.strftime(datetime.strptime(note.date, '%Y%m%d'), '%Y-%m-%d')
    fill.footer.show_meta(date)

def command_add_contact(contact_obj):
    fill.invoke_console('add', contact_obj)

def command_rename_contact(contact_obj):
    data = {'name': str(contact_obj._w.original_widget.text)}
    fill.invoke_console('rename', contact_obj, None, data)

def command_delete_contact(contact_obj):
    data = {'name': str(contact_obj._w.original_widget.text)}
    fill.invoke_console('delete', contact_obj, None, data)

def command_search_contact(contact_obj):
    fill.invoke_console('search', contact_obj)

def command_add_attribute(contact_obj, attr_obj):
    data = {'name': contact_obj.name,
            'key': attr_obj.key,
            'value': attr_obj.value}
    fill.invoke_console('add-attribute', contact_obj, attr_obj, data)

def command_edit_attribute(contact_obj, attr_obj):
    data = {'name': contact_obj.name,
            'key': attr_obj.key,
            'value': attr_obj.value}
    fill.invoke_console('edit-attribute', contact_obj, attr_obj, data)

def command_set_gift_given(contact_obj, attr_obj):
    data = {'value': attr_obj.value,
            'new_value': "x " + attr_obj.value}
    fill.invoke_console('set-gift-given', contact_obj, attr_obj, data)

def command_set_gift_not_given(contact_obj, attr_obj):
    data = {'value': attr_obj.value,
            'new_value': attr_obj.value[2:]}
    fill.invoke_console('set-gift-not-given', contact_obj, attr_obj, data)

def command_delete_attribute(contact_obj, attr_obj):
    data = {'name': contact_obj.name,
            'key': attr_obj.key,
            'value': attr_obj.value}
    fill.invoke_console('delete-attribute', contact_obj, attr_obj, data)

def command_add_note(contact_obj):
    data = {'date': datetime.strftime(date.today(), "%Y%m%d")}
    fill.invoke_console('add-note', contact_obj, None, data)

def command_edit_note(contact_obj, attr_obj):
    data = {'date': attr_obj.date}
    fill.invoke_console('edit-note', contact_obj, attr_obj, data)

def command_delete_note(contact_obj, attr_obj):
    data = {'date': attr_obj.date}
    fill.invoke_console('delete-note', contact_obj, attr_obj, data)


# urwid classes


class MyHeader(urwid.Padding):
    def __init__(self, contact_name=None):
        super(MyHeader, self).__init__(urwid.Text(''), align='left', left=NAV_WIDTH+1)
    def set_path(self, path):
        self.base_widget.set_text(path)
    def show_contact_name(self, name):
        self.set_path(name)

class MyCommandLine(urwid.Filler):
    def __init__(self):
        super(MyCommandLine, self).__init__(urwid.Text(""))
        self.command = ""
    def invoke_console(self, command, contact_obj, attr_obj=None, data=None):
        self.command = command
        self.contact_obj = contact_obj
        self.attr_obj = attr_obj
        self.data = data
        # commands without console interaction
#        if command in ('set-gift-given'):
#            msg = set_gift_given(self.contact_obj, self.attr_obj)
#            self.original_widget = urwid.Text(msg)
#            fill.set_focus('body')
        # commands with console interaction
        if command in ('search'):
            self.show_console('/')
        elif command in ('add'):
            self.show_console(':', "{} ".format(command))
        elif command in ('rename', 'edit', 'rn', 'remove', 'delete', 'rm', 'del'):
            self.show_console(':', "{} {}".format(command, data['name']))
        elif command in ('add-attribute'):
            self.show_console(':', "{} ".format(command))
        elif command in ('edit-attribute'):
            self.show_console(':', "{} {}".format(command, data['value']))
        elif command in ('set-gift-given'):
            self.show_console(':', "{} {}".format('edit-attribute', data['new_value']))
        elif command in ('set-gift-not-given'):
            self.show_console(':', "{} {}".format('edit-attribute', data['new_value']))
        elif command in ('delete-attribute'):
            self.show_console(':', "{} {} {}".format(command, data['key'], data['value']))
        elif command in ('add-note'):
            self.show_console('date=', "{}".format(data['date']))
        elif command in ('edit-note'):
            self.show_console(':', "{} {}".format(command, data['date']))
        elif command in ('delete-note'):
            self.show_console(':', "{} {}".format(command, data['date']))
        else:
            self.show_console(':', "{} ".format(command))
    def show_message(self, message):
        self.body = urwid.Text(message)
    def show_console(self, caption, edit_text=''):
        self.body = urwid.Edit(caption, edit_text)
    def show_meta(self, meta):
        self.body = urwid.AttrMap(urwid.Text(meta, 'right'), 'status_bar')
    def keypress(self, size, key):
        if key == 'esc':
            fill.init_footer()
            fill.set_focus('body')
        if key != 'enter':
            return super(MyCommandLine, self).keypress(size, key)
        args = self.original_widget.edit_text.split()
        if self.command == 'search':
            name = " ".join(args[0:])
            msg = search_contact(name)
        elif self.command == 'add-note':
            date = " ".join(args[0:])
            try:
                date_object = datetime.strptime(date, '%Y%m%d')
                msg = add_note(self.contact_obj, self.attr_obj, date_object)
            except ValueError:
                msg = [date, " not a valid date."]
        elif self.command == 'edit-note':
            date = " ".join(args[1:])
            try:
                date_object = datetime.strptime(date, '%Y%m%d')
                msg = edit_note(self.contact_obj, self.attr_obj, date_object)
            except ValueError:
                msg = [date, " not a valid date."]
        elif self.command == 'delete-note':
            date = " ".join(args[1:])
            try:
                date_object = datetime.strptime(date, '%Y%m%d')
                msg = delete_note(self.contact_obj, self.attr_obj, date_object)
            except ValueError:
                msg = [date, " not a valid date."]
        else:
            command = args[0]
            if command in ('add'):
                name = " ".join(args[1:])
                msg = add_contact(name)
            elif command in ('rename', 'edit', 'rn'):
                old_name = self.data['name']
                new_name = " ".join(args[1:])
                msg = rename_contact(self.contact_obj, old_name, new_name)
            elif command in ('remove', 'delete', 'rm', 'del'):
                name = " ".join(args[1:])
                msg = delete_contact(self.contact_obj)
            elif command in ('add-attribute'):
                key = args[1]
                value = " ".join(args[2:])
                msg = add_attribute(self.contact_obj, key, value)
            elif command in ('edit-attribute'):
                old_value = self.data['value']
                new_value = " ".join(args[1:])
                msg = edit_attribute(self.contact_obj, self.attr_obj, old_value, new_value)
            elif command in ('delete-attribute'):
                key = args[1]
                value = " ".join(args[2:])
                msg = delete_attribute(self.contact_obj, self.attr_obj, key, value)
            else:
                msg = 'Not a valid command.'
        self.original_widget = urwid.Text(msg)
        fill.set_focus('body')


class MyListBox(urwid.ListBox):
    def __init__(self, listwalker):
        super(MyListBox, self).__init__(listwalker)
        self.repeat_command = 0
    def keypress(self, size, key):
        if key == 't':
            if self.repeat_command > 0:
                self.jump_down(size, self.repeat_command)
                self.repeat_command = 0
            else:
                super(MyListBox, self).keypress(size, 'down')
        elif key == 'r':
            if self.repeat_command > 0:
                self.jump_up(size, self.repeat_command)
                self.repeat_command = 0
            else:
                super(MyListBox, self).keypress(size, 'up')
        elif key == 'G':
            super(MyListBox, self).keypress(size, 'end')
            super(MyListBox, self).keypress(size, 'end')
        elif key == 'g':
            super(MyListBox, self).keypress(size, 'home')
        elif key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if self.repeat_command > 0:
                self.repeat_command = int(str(self.repeat_command) + key)
            else:
                self.repeat_command = int(key)
        else:
            return super(MyListBox, self).keypress(size, key)
    def jump_down(self, size, n):
        for i in range(0, n):
            super(MyListBox, self).keypress(size, 'down')
    def jump_up(self, size, n):
        for i in range(0, n):
            super(MyListBox, self).keypress(size, 'up')


class MyContactDetails(MyListBox):
    def __init__(self, contact_obj):
        listwalker = urwid.SimpleFocusListWalker([])
        self.contact = contact_obj
        super(MyContactDetails, self).__init__(listwalker)
    def load_contacts_details(self):
        a = []
        a.append(MyContactAttribute(self.contact.name, show_contact_details,
            self.contact, "givenName", self.contact.name))
        a.append(urwid.Divider())
        if contains_contact(self.contact.name):
            for c in get_contact_info(self.contact):
                c_string = c[0] + ': ' + c[1]
                a.append(MyContactAttribute(c_string, show_contact_details,
                    self.contact, c[0], c[1]))
            if has_gifts(self.contact):
                if len(a) > 2:
                    a.append(urwid.Divider())
                a.append(urwid.Text(u"GESCHENKE"))
                for c in get_contact_gifts(self.contact):
                    a.append(MyContactGift(c, show_contact_details,
                        self.contact, c))
        if len(a) > 2:
            a.append(urwid.Divider())
        if has_notes(self.contact):
            a.append(urwid.Text(u"NOTIZEN"))
            for key, value in get_contact_notes(self.contact).items():
                date_object = datetime.strptime(key, '%Y%m%d')
                date = datetime.strftime(date_object, '%d-%m-%Y')
                a.append(MyContactNote(value, show_contact_details,
                    self.contact, key, value))
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, 'modified', self.show_attributes_meta)
    def keypress(self, size, key):
        if key == 'd':
            return super(MyContactDetails, self).keypress(size, 'left')
        else:
            return super(MyContactDetails, self).keypress(size, key)
    def show_attributes_meta(self):
        if isinstance(self.focus, MyContactNote):
            show_attributes_meta(self.focus)
        else:
            fill.init_footer()

class MyContactAttribute(urwid.Button):
    def __init__(self, caption, callback, contact_obj, key, value):
        super(MyContactAttribute, self).__init__(caption)
        self.contact_obj = contact_obj
        self.key = key
        self.value = value
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, len(key)+len(value)+3), None, 'selected')
    def keypress(self, size, key):
        if key == 'i':
            command_add_attribute(self.contact_obj, self)
        elif key == 'a':
            command_edit_attribute(self.contact_obj, self)
        elif key == 'h':
            command_delete_attribute(self.contact_obj, self)
        elif key == 'y':
            pyperclip.copy(self.value)
            fill.show_message("Copied \"" + self.value + "\" to clipboard.")
        else:
            return super(MyContactAttribute, self).keypress(size, key)

class MyContactGift(MyContactAttribute):
    def __init__(self, caption, callback, contact_obj, value):
        super(MyContactGift, self).__init__(caption, callback, contact_obj, 'giftIdea', value)
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, len(value)+1), None, 'selected')
    def keypress(self, size, key):
        if key == 'x':
            command_set_gift_given(self.contact_obj, self)
        elif key == 'X':
            command_set_gift_not_given(self.contact_obj, self)
        else:
            return super(MyContactGift, self).keypress(size, key)

class MyContactNote(urwid.Button):
    def __init__(self, caption, callback, contact_obj, date, text):
        super(MyContactNote, self).__init__(caption)
        self.contact_obj = contact_obj
        self.date = date
        self.text = text
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, len(text)+1), None, 'selected')
    def keypress(self, size, key):
        if key == 'i':
            command_add_attribute(self.contact_obj, self)
        elif key == 'e':
            command_edit_note(self.contact_obj, self)
        elif key == 'h':
            command_delete_note(self.contact_obj, self)
        else:
            return super(MyContactNote, self).keypress(size, key)

class MyContact(urwid.Button):
    def __init__(self, caption, callback):
        super(MyContact, self).__init__(caption)
        urwid.connect_signal(self, 'click', callback)
        self.name = caption
        #name = contact._w.original_widget.text
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, 100), None, 'selected')


class MyContactList(MyListBox):
    def __init__(self):
        listwalker = urwid.SimpleFocusListWalker([])
        super(MyContactList, self).__init__(listwalker)
    #TODO: saubere Positionsreaktionen auf rename, add und delete
    def load_contacts(self, renamed_contact=None, focus_details=False):
        focus_pos = 0
        focus_contact = None
        if self.body:
            focus_contact = self.focus.label
        a = []
        for c in get_contact_list():
            a.append(MyContact(c, show_contact_details))
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, 'modified', self.show_contact)
        if focus_contact:
            focus_pos = self.get_contact_position(focus_contact)
        if renamed_contact:
            focus_pos = self.get_contact_position(renamed_contact)
        #special case: deleted last one
        if focus_pos == None:
            focus_pos = len(self.body) - 1
        self.set_focus(focus_pos)
        #when details were edited
        #TODO if details are shown: refresh the attributes, gifts and notes of the focus
    def keypress(self, size, key):
        if key == 'n':
            return super(MyContactList, self).keypress(size, 'right')
        elif key == 'a':
            command_rename_contact(self.focus)
        elif key == 'i':
            command_add_contact(self.focus)
        elif key == 'h':
            command_delete_contact(self.focus)
        elif key == '/':
            command_search_contact(self.focus)
        else:
            return super(MyContactList, self).keypress(size, key)
    def get_contact_position(self, name):
        pos = 0
        for entry in self.body:
            if entry.label.startswith(name):
                return pos
            pos = pos + 1
        return None
    def jump_to_contact(self, name):
        pos = self.get_contact_position(name)
        if pos is not None:
            self.set_focus(pos)
    def show_contact(self):
        show_contact_details(self.focus)


class MyColumns(urwid.Columns):
    def __init__(self):
        super(MyColumns, self).__init__([], dividechars=1)
        self.focused_contact = None
        self.focused_attribute = None
    def show_contact_index(self):
        contact_list = MyContactList()
        contact_list.load_contacts()
        self.contents.append((urwid.AttrMap(contact_list, 'options', focus_map),
            self.options('given', NAV_WIDTH)))
        self.focus_position = 0
    def open_contact_details(self, contact):
        self.focused_contact = contact
        if len(self.contents) > 1:
            del self.contents[1]
        contact_list = MyContactDetails(contact)
        contact_list.load_contacts_details()
        self.contents.append((urwid.AttrMap(contact_list, 'options', focus_map),
            self.options('weight', 1, True)))
    def keypress(self, size, key):
        if key == 'ctrl r':
            reload_contact_list(self.focused_contact, self.focused_attribute)
        elif key == 'j':
            command_add_note(self.focused_contact)
        else:
            return super(MyColumns, self).keypress(size, key)


class MyFrame(urwid.Frame):
    def __init__(self):
        super(MyFrame, self).__init__(None)
        self.header = MyHeader()
        self.init_footer()
    def init_footer(self):
        self.footer = urwid.BoxAdapter(MyCommandLine(), height=1)
    def set_body(self):
        index_columns = MyColumns()
        index_columns.show_contact_index()
        self.body = index_columns
    def invoke_console(self, command, contact_obj, attribute_obj=None, data=None):
        self.footer.invoke_console(command, contact_obj, attribute_obj, data)
        fill.set_focus('footer')
    def show_message(self, message):
        self.footer.show_message(message)
    def reload_contact_list(self, focused_contact, focused_attr):
        self.body.contents[0][0].base_widget.load_contacts()
    def show_contact_details(self, contact):
        #self.header.show_contact_name(contact.name)
        if self.body is not None:
            self.body.open_contact_details(contact)



g = load_file(CONTACTS_PATH)

fill = MyFrame()
fill.set_body()

loop = urwid.MainLoop(fill, palette, unhandled_input=show_or_exit)
loop.run()

