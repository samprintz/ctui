from rdflib import Graph
from rdflib import URIRef
from rdflib.namespace import RDF

import urwid
import curses

import operator

class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            [u' ', caption], 1), None, 'selected')
            #[u'  \N{BULLET} ', caption], 2), None, 'selected')

class SubMenu(urwid.WidgetWrap):
    def __init__(self, caption, choices):
        super(SubMenu, self).__init__(MenuButton(
            [caption, u"\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        line = urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}')
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.AttrMap(urwid.Text([u"\n  ", caption]), 'heading'),
            urwid.AttrMap(line, 'line'),
            urwid.Divider()] + choices + [urwid.Divider()]))
        self.menu = urwid.AttrMap(listbox, 'options')
        self.caption = caption

    def open_menu(self, button):
        top.open_box(self.menu)

class Choice(urwid.WidgetWrap):
    def __init__(self, caption):
        super(Choice, self).__init__(
            MenuButton(caption, self.item_chosen))
        self.caption = caption

    def item_chosen(self, button):
        response = urwid.Text([u'  You chose ', self.caption, u'\n'])
        done = MenuButton(u'Ok', exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        top.open_box(urwid.AttrMap(response_box, 'options'))

def exit_program(key):
    raise urwid.ExitMainLoop()


palette = [
    (None,  'light gray', 'black'),
    ('heading', 'light gray', 'black'),
    ('line', 'black', 'black'),
    ('options', 'light gray', 'black'),
    ('focus heading', 'white', 'black'),
    ('focus line', 'black', 'black'),
    ('focus options', 'white', 'black'),
    ('selected', 'white', 'dark blue')]
focus_map = {
    'heading': 'focus heading',
    'options': 'focus options',
    'line': 'focus line'}

class HorizontalBoxes(urwid.Columns):
    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map),
            self.options('given', 24)))
        self.focus_position = len(self.contents) - 1

def navigation(key):
    txt.set_text(repr(key))







g = Graph()
g.parse("contacts.n3", format="n3")

#for subject,predicate,obj in g:

givenName = URIRef('http://hiea.de/contact#givenName')

contact_menu = []
for s,p,o in g.triples( (None, givenName, None) ):
    # attributes
    # TODO make unique (giftIdea only once)
    attributes = []
    for s2,p2,o2 in g.triples( (s, None, None) ):
        # values
        values = []
        for s3,p3,o3 in g.triples( (s, p2, None) ):
            value = Choice(str(o3))
            values.append(value)
        values.sort(key=operator.attrgetter('caption'))
        attribute_menu = SubMenu(str(p2.split("#",1)[1]), values)
        attributes.append(attribute_menu)
    attributes.sort(key=operator.attrgetter('caption'))
    menu_entry = SubMenu(str(o), attributes)
    contact_menu.append(menu_entry)
contact_menu.sort(key=operator.attrgetter('caption'))


menu_top = SubMenu(u'Contacts', contact_menu)

'''
menu_top = SubMenu(u'Main Menu', [
    SubMenu(u'Applications', [
        SubMenu(u'Accessories', [
            Choice(u'Text Editor'),
            Choice(u'Terminal'),
        ]),
    ]),
    SubMenu(u'System', [
        SubMenu(u'Preferences', [
            Choice(u'Appearance'),
        ]),
        Choice(u'Lock Screen'),
    ]),
])
'''


top = HorizontalBoxes()
top.open_box(menu_top.menu)
txt = urwid.Text(u"Hello World")
fill2 = urwid.Filler(txt, 'top')
fill = urwid.Filler(top, valign='top', height=('relative', 100))
urwid.MainLoop(fill, palette, unhandled_input=navigation).run()



#g.serialize(format='n3', indent=True, destination='test.n3')
