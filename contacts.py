from rdflib import *
from rdflib.resource import *
import operator
import pudb
import urwid

PATH = 'test.n3'
GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
NAV_WIDTH = 24
DETAILS_WIDTH = 48

palette = [
    (None,  'light gray', 'black'),
    ('heading', 'black', 'light gray'),
    ('line', 'black', 'light gray'),
    ('options', 'light gray', 'black'),
    ('focus heading', 'white', 'dark red'),
    ('focus line', 'black', 'dark red'),
    ('focus options', 'black', 'light gray'),
    ('selected', 'black', 'light gray')]

focus_map = {
    'heading': 'focus heading',
    'options': 'focus options',
    'line': 'focus line'}


### N3 functions

def load_file(path):
    g = Graph()
    g.parse(path, format="n3")
    return g

def save_file(path):
    g.serialize(format='n3', indent=True, destination=path)

def contains_contact(name):
    return (None, GIVEN_NAME_REF, Literal(name)) in g

def get_contact_list():
    contacts = []
    for o in g.objects(None, GIVEN_NAME_REF):
        contacts.append(str(o))
    return sorted(contacts)

def get_contact_details(name):
    details = []
    s = next(g.subjects(GIVEN_NAME_REF, Literal(name)))
    for p,o in g.predicate_objects(s):
        p_string = p.split('#',1)[1]
        if p_string == 'givenName': continue
        details.append(p_string + ': ' + str(o))
    return sorted(details)



# "backend" functions / operations

def rename_contact(current_contact, old_name, new_name):
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
            save_file(PATH)
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
        save_file(PATH)
        # reload urwid
        fill.body.contents[0][0].base_widget.load_contacts()
        return [name, " added."]


def delete_contact(current_contact, name):
    if contains_contact(name):
        # update n3
        g.remove( (None, GIVEN_NAME_REF, Literal(name)) )
        save_file(PATH)
        # update urwid
        fill.body.contents[0][0].base_widget.load_contacts()
        return [name, " deleted."]
    else:
        return ["Error: ", name, " doesn't exists."]

def search_contact(name):
    fill.body.contents[0][0].base_widget.jump_to_contact(name)
    return ""



# urwid functions

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

#TODO
def reload_contact_list():
    pass

def show_contact_details(contact):
    name = contact._w.original_widget.text
    fill.header.show_contact_name(name)
    if fill.body is not None:
        fill.body.open_contact_details(name)


def command_add():
    MyCommandLine('add')

def command_rename(executing_widget):
    data = {'name': str(executing_widget._w.original_widget.text)}
    MyCommandLine('rename', executing_widget, data)

def command_delete(executing_widget):
    data = {'name': str(executing_widget._w.original_widget.text)}
    MyCommandLine('delete', executing_widget, data)

def command_search():
    MyCommandLine('search')




# urwid classes


class MyHeader(urwid.Padding):
    def __init__(self, contact_name=None):
        super(MyHeader, self).__init__(urwid.Text(''), align='left', left=NAV_WIDTH)
    def set_path(self, path):
        self.base_widget.set_text(path)
    def show_contact_name(self, name):
        self.set_path(name)

class MyCommandLine(urwid.Filler):
    def __init__(self, command=None, executing_widget=None, data=None):
        super(MyCommandLine, self).__init__(None)
        self.executing_widget = executing_widget
        self.command = command
        self.data = data

        if command in ('add'):
            self.body = urwid.Edit(caption=u":", edit_text="{} "
                    .format(command))
        elif command in ('search'):
            self.body = urwid.Edit(caption=u"/")
        else:
        #if command in ('rename', 'edit', 'rn', 'remove', 'delete', 'rm', 'del'):
            self.body = urwid.Edit(caption=u":", edit_text="{} {}"
                    .format(command, data['name']))

        fill.footer = urwid.BoxAdapter(self, height=1)
        fill.set_focus('footer')

    def keypress(self, size, key):
        if key == 'esc':
            fill.footer = None
            fill.set_focus('body')
        if key != 'enter':
            return super(MyCommandLine, self).keypress(size, key)
        args = self.original_widget.edit_text.split()
        if self.command == 'search':
            name = " ".join(args[0:])
            msg = search_contact(name)
        else:
            command = args[0]
            if command in ('add'):
                name = " ".join(args[1:])
                msg = add_contact(name)
            elif command in ('rename', 'edit', 'rn'):
                old_name = self.data['name']
                new_name = " ".join(args[1:])
                msg = rename_contact(self.executing_widget, old_name, new_name)
            elif command in ('remove', 'delete', 'rm', 'del'):
                name = " ".join(args[1:])
                msg = delete_contact(self.executing_widget, name)
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
        elif key == 'a':
            command_rename(self.focus)
        elif key == 'i':
            command_add()
        elif key == 'h':
            command_delete(self.focus)
        elif key == '/':
            command_search()
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
    def __init__(self, contact):
        listwalker = urwid.SimpleFocusListWalker([])
        self.contact = contact
        super(MyContactDetails, self).__init__(listwalker)
    def load_contacts_details(self):
        a = []
        for c in get_contact_details(self.contact):
            a.append(MyContact(c, show_contact_details))
        self.body = urwid.SimpleFocusListWalker(a)
    def keypress(self, size, key):
        if key == 'd':
            return super(MyContactDetails, self).keypress(size, 'left')
        else:
            return super(MyContactDetails, self).keypress(size, key)

class MyContact(urwid.Button):
    def __init__(self, caption, callback):
        super(MyContact, self).__init__(caption)
        urwid.connect_signal(self, 'click', callback)
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, 100), None, 'selected')
    def rename(self, new_name):
        super(MyContact, self).__init__(new_name) 
        urwid.connect_signal(self, 'click', show_contact_details)
        # remove the arrows of the default button style
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            new_name, 100), None, 'selected')


class MyContactList(MyListBox):
    def __init__(self):
        listwalker = urwid.SimpleFocusListWalker([])
        super(MyContactList, self).__init__(listwalker)
    #TODO: saubere Positionsreaktionen auf rename, add und delete
    def load_contacts(self, renamed_contact=None):
        focus_pos = 0
        focus_contact = None
        if self.body:
            focus_contact = self.focus.label
        a = []
        for c in get_contact_list():
            a.append(MyContact(c, show_contact_details))
        self.body = urwid.SimpleFocusListWalker(a)
        urwid.connect_signal(self.body, "modified", self.show_contact)
        if focus_contact:
            focus_pos = self.get_contact_position(focus_contact)
        if renamed_contact:
            focus_pos = self.get_contact_position(renamed_contact)
        #special case: deleted last one
        if focus_pos == None:
            focus_pos = len(self.body) - 1
        self.set_focus(focus_pos)
    def keypress(self, size, key):
        if key == 'n':
            return super(MyContactList, self).keypress(size, 'right')
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
    def show_contact_index(self):
        contact_list = MyContactList()
        contact_list.load_contacts()
        self.contents.append((urwid.AttrMap(contact_list, 'options', focus_map),
            self.options('given', NAV_WIDTH)))
        self.focus_position = 0
    def open_contact_details(self, contact):
        if len(self.contents) > 1:
            del self.contents[1]
        contact_list = MyContactDetails(contact)
        contact_list.load_contacts_details()
        self.contents.append((urwid.AttrMap(contact_list, 'options', focus_map),
            self.options('given', DETAILS_WIDTH)))


class MyFrame(urwid.Frame):
    def __init__(self):
        super(MyFrame, self).__init__(None)
        self.header = MyHeader()
    def set_body(self):
        index_columns = MyColumns()
        index_columns.show_contact_index()
        self.body = index_columns
    def set_footer(self, footer):
        self.footer = footer
    def set_header(self, header):
        self.header = header


g = load_file(PATH)

fill = MyFrame()
fill.set_body()

loop = urwid.MainLoop(fill, palette, unhandled_input=show_or_exit)
loop.run()

