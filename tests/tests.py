import unittest

import ctui.util as util
from ctui.cli import Mode, Action
from ctui.component.contact_entry import ContactEntry
from ctui.component.detail_entry import AttributeEntry, GiftEntry, NoteEntry
from ctui.core import *
from ctui.objects import *
from ctui.ui import UI

CONFIG_FILE = 'files/config.ini'
config = util.load_config(CONFIG_FILE)


class TestCore(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.core = Core(config, True)
        self.name1 = "Test Contact A"
        self.name2 = "Test Contact B"
        self.contact1 = Contact(self.name1, self.core)
        self.contact2 = Contact(self.name2, self.core)

    @classmethod
    def setUp(self):
        pass

    # contacts

    def test_get_all_contact_names(self):
        contact_names = self.core.get_all_contact_names()
        self.assertIsNotNone(contact_names)
        self.assertIsInstance(contact_names, list)

    def test_add_contact(self):
        res = self.core.add_contact(self.contact1)
        self.assertTrue(self.core.contains_contact(self.contact1))

    def test_add_contact_already_existing(self):
        self.core.add_contact(self.contact1)
        res = self.core.add_contact(self.contact1)
        self.assertTrue(res.startswith("Error"))
        self.assertTrue(self.core.contains_contact(self.contact1))

    def test_add_contact_already_existing_notes(self):
        self.core.textfilestore.add_contact(self.contact1)
        res = self.core.add_contact(self.contact1)
        self.assertTrue(res.startswith("Error"))
        self.assertTrue(self.core.contains_contact(self.contact1))

    def test_add_contact_already_existing_rdf(self):
        self.core.rdfstore.add_contact(self.contact1)
        res = self.core.add_contact(self.contact1)
        self.assertTrue(res.startswith("Error"))
        self.assertTrue(self.core.contains_contact(self.contact1))

    def test_rename_contact(self):
        self.core.add_contact(self.contact1)
        res = self.core.rename_contact(self.contact1, self.name2)
        self.assertFalse(self.core.contains_contact_name(self.name1))
        self.assertTrue(self.core.contains_contact_name(self.name2))

    def test_rename_contact_unchanged(self):
        self.core.add_contact(self.contact1)
        res = self.core.rename_contact(self.contact1, self.name1)
        self.assertTrue(res.startswith("Warning"))
        self.assertTrue(self.core.contains_contact_name(self.name1))

    def test_rename_contact_not_existing(self):
        self.assertFalse(self.core.contains_contact_name(self.name1))
        res = self.core.rename_contact(self.contact1, self.name2)
        self.assertTrue(res.startswith("Error"))
        self.assertFalse(self.core.contains_contact_name(self.name2))

    def test_rename_contact_with_only_notes(self):
        self.core.textfilestore.add_contact(self.contact1)
        self.assertFalse(self.core.rdfstore.contains_contact(self.contact1))
        res = self.core.rename_contact(self.contact1, self.name2)
        self.assertTrue(self.core.contains_contact_name(self.name2))
        self.assertTrue(
            self.core.textfilestore.contains_contact_name(self.name2))
        self.assertFalse(self.core.rdfstore.contains_contact_name(self.name2))
        self.assertFalse(self.core.contains_contact_name(self.name1))
        self.assertFalse(
            self.core.textfilestore.contains_contact_name(self.name1))
        self.assertFalse(self.core.rdfstore.contains_contact_name(self.name1))

    def test_rename_contact_with_only_rdf(self):
        self.core.rdfstore.add_contact(self.contact1)
        self.assertFalse(
            self.core.textfilestore.contains_contact(self.contact1))
        res = self.core.rename_contact(self.contact1, self.name2)
        self.assertTrue(self.core.contains_contact_name(self.name2))
        self.assertTrue(self.core.rdfstore.contains_contact_name(self.name2))
        self.assertFalse(
            self.core.textfilestore.contains_contact_name(self.name2))
        self.assertFalse(self.core.contains_contact_name(self.name1))
        self.assertFalse(self.core.rdfstore.contains_contact_name(self.name1))
        self.assertFalse(
            self.core.textfilestore.contains_contact_name(self.name1))

    def test_delete_contact(self):
        self.core.add_contact(self.contact1)
        res = self.core.delete_contact(self.contact1)
        self.assertFalse(self.core.contains_contact(self.contact1))
        self.assertFalse(self.core.rdfstore.contains_contact(self.contact1))
        self.assertFalse(
            self.core.textfilestore.contains_contact(self.contact1))

    def test_delete_contact_not_existing(self):
        self.assertFalse(self.core.contains_contact(self.contact1))
        res = self.core.delete_contact(self.contact1)
        self.assertTrue(res.startswith("Error"))

    def test_delete_contact_with_only_notes(self):
        self.core.textfilestore.add_contact(self.contact1)
        res = self.core.delete_contact(self.contact1)
        self.assertFalse(self.core.contains_contact(self.contact1))
        self.assertFalse(self.core.rdfstore.contains_contact(self.contact1))
        self.assertFalse(
            self.core.textfilestore.contains_contact(self.contact1))

    def test_delete_contact_with_only_rdf(self):
        self.core.rdfstore.add_contact(self.contact1)
        res = self.core.delete_contact(self.contact1)
        self.assertFalse(self.core.contains_contact(self.contact1))
        self.assertFalse(self.core.rdfstore.contains_contact(self.contact1))
        self.assertFalse(
            self.core.textfilestore.contains_contact(self.contact1))

    def test_delete_contact_with_attributes(self):
        self.core.rdfstore.add_contact(self.contact1)
        attr = Attribute("key", "value")
        self.contact1.add_attribute(attr)
        self.assertTrue(self.core.rdfstore.has_attribute(self.contact1, attr))
        res = self.core.delete_contact(self.contact1)
        self.assertFalse(self.core.contains_contact(self.contact1))
        self.assertFalse(self.core.rdfstore.contains_attribute(attr))

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact1)
        self.core.delete_contact(self.contact2)

    @classmethod
    def tearDownClass(self):
        pass


class TestObjects(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.core = Core(config, True)
        self.name = "Test Contact"
        self.contact = Contact(self.name, self.core)
        self.attr_key1 = "key1"
        self.attr_key2 = "key2"
        self.attr_value1 = "Attribute 1"
        self.attr_value2 = "Attribute 2"
        self.attr1 = Attribute(self.attr_key1, self.attr_value1)
        self.attr2 = Attribute(self.attr_key2, self.attr_value2)
        self.gift_name1 = "Gift 1"
        self.gift_name2 = "Gift 2"
        self.gift1 = Gift(self.gift_name1)
        self.gift2 = Gift(self.gift_name2)
        self.note_name1 = "19990101"
        self.note_name2 = "19991215"
        self.date1 = datetime.strptime(self.note_name1, '%Y%m%d')
        self.date2 = datetime.strptime(self.note_name2, '%Y%m%d')
        self.note_name_invalid = "1248"
        self.note_content1 = "Text 1"
        self.note_content2 = "Text 2"
        self.note1 = Note(self.date1, self.note_content1)

    @classmethod
    def setUp(self):
        self.core.add_contact(self.contact)

    # attributes

    def test_add_attr(self):
        res = self.contact.add_attribute(self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(self.contact.has_attribute(self.attr1))

    def test_add_attr_already_existing(self):
        self.contact.add_attribute(self.attr1)
        self.assertTrue(self.contact.has_attribute(self.attr1))
        res = self.contact.add_attribute(self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(self.contact.has_attribute(self.attr1))

    def test_edit_attr(self):
        self.contact.add_attribute(self.attr1)
        res = self.contact.edit_attribute(self.attr1, self.attr2)
        self.assertIsNotNone(res)
        self.assertFalse(self.contact.has_attribute(self.attr1))
        self.assertTrue(self.contact.has_attribute(self.attr2))

    def test_edit_attr_unchanged(self):
        self.contact.add_attribute(self.attr1)
        res = self.contact.edit_attribute(self.attr1, self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Warning"))
        self.assertTrue(self.contact.has_attribute(self.attr1))

    def test_edit_attr_not_existing(self):
        self.assertFalse(self.contact.has_attribute(self.attr1))
        res = self.contact.edit_attribute(self.attr1, self.attr2)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Error"))
        self.assertFalse(self.contact.has_attribute(self.attr2))

    def test_edit_attr_givenname_with_only_notes(self):
        self.core.delete_contact(self.contact)  # undo setUp
        self.core.textfilestore.add_contact(self.contact)
        self.assertFalse(self.core.rdfstore.contains_contact(self.contact))
        new_name = "Test Person"
        old_attr = Attribute("givenName", self.name)
        new_attr = Attribute("givenName", new_name)
        res = self.contact.edit_attribute(old_attr, new_attr)
        self.assertTrue(self.core.contains_contact_name(new_name))
        self.assertFalse(self.core.contains_contact_name(self.name))
        self.assertFalse(self.core.rdfstore.contains_contact_name(new_name))
        self.core.contact_list = self.core.get_all_contacts()  # to be able to delete it by name
        self.core.delete_contact_by_name(new_name)

    def test_delete_attr(self):
        self.contact.add_attribute(self.attr1)
        self.assertTrue(self.contact.has_attribute(self.attr1))
        res = self.contact.delete_attribute(self.attr1)
        self.assertIsNotNone(res)
        self.assertFalse(self.contact.has_attribute(self.attr1))

    def test_delete_attr_not_existing(self):
        self.assertFalse(self.contact.has_attribute(self.attr1))
        res = self.contact.delete_attribute(self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Error"))

    # gifts

    def test_add_gift(self):
        res = self.contact.add_gift(self.gift1)
        self.assertIsNotNone(res)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))

    def test_add_gift_already_existing(self):
        self.contact.add_gift(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.add_gift(self.gift1)
        self.assertIsNotNone(res)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))

    def test_edit_gift(self):
        self.contact.add_gift(self.gift1)
        res = self.contact.edit_gift(self.gift1, self.gift2)
        self.assertIsNotNone(res)
        self.assertFalse(self.contact.has_gift(self.gift1.get_id()))
        self.assertTrue(self.contact.has_gift(self.gift2.get_id()))

    def test_edit_gift_unchanged(self):
        self.contact.add_gift(self.gift1)
        res = self.contact.edit_gift(self.gift1, self.gift1)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Warning"))
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))

    def test_mark_gifted(self):
        self.gift1.gifted = False
        self.contact.add_gift(self.gift1)
        self.contact.mark_gifted(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.get_gift(self.gift1.get_id())
        self.assertTrue(res.gifted)

    def test_unmark_gifted(self):
        self.gift1.gifted = True
        self.contact.add_gift(self.gift1)
        self.contact.unmark_gifted(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.get_gift(self.gift1.get_id())
        self.assertFalse(res.gifted)

    def test_mark_permanent(self):
        self.gift1.permanent = False
        self.contact.add_gift(self.gift1)
        self.contact.mark_permanent(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.get_gift(self.gift1.get_id())
        self.assertTrue(res.permanent)

    def test_unmark_permanent(self):
        self.gift1.permanent = True
        self.contact.add_gift(self.gift1)
        self.contact.unmark_permanent(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.get_gift(self.gift1.get_id())
        self.assertFalse(res.permanent)

    def test_edit_gift_not_existing(self):
        self.assertFalse(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.edit_gift(self.gift1, self.gift2)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Error"))
        self.assertFalse(self.contact.has_gift(self.gift2.get_id()))

    def test_delete_gift(self):
        self.contact.add_gift(self.gift1)
        self.assertTrue(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.delete_gift(self.gift1)
        self.assertIsNotNone(res)
        self.assertFalse(self.contact.has_gift(self.gift1.get_id()))

    def test_delete_gift_not_existing(self):
        self.assertFalse(self.contact.has_gift(self.gift1.get_id()))
        res = self.contact.delete_gift(self.gift1)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Error"))

    # notes

    def test_add_note_new_dir(self):
        self.assertFalse(self.core.textfilestore.contains_contact(self.contact))
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertTrue(self.contact.has_note(self.date1))

    def test_add_note_existing_dir(self):
        self.core.textfilestore.add_contact(self.contact)
        self.assertTrue(self.core.textfilestore.contains_contact(self.contact))
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertTrue(self.contact.has_note(self.date1))

    def test_add_note_date_error(self):
        pass

    def test_add_note_already_existing(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertTrue(self.contact.has_note(self.date1))
        with self.assertRaises(AssertionError):
            self.core.textfilestore.add_note(self.contact, self.note1)

    def test_rename_note(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.core.textfilestore.rename_note(self.contact.get_id(), self.note1,
                                            self.date2)
        self.assertTrue(self.contact.has_note(self.date2))
        self.assertFalse(self.contact.has_note(self.date1))

    def test_rename_note_date_error(self):
        pass

    def test_rename_note_unchanged(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        with self.assertRaises(AssertionError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1,
                                                self.date1)
        self.assertTrue(self.contact.has_note(self.date1))

    def test_rename_note_not_existing(self):
        self.assertFalse(self.contact.has_note(self.date1))
        with self.assertRaises(AssertionError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1,
                                                self.date2)
        self.assertFalse(self.contact.has_note(self.date1))

    def test_rename_note_already_existing(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        note2 = Note(self.date2, self.note_content2)
        self.core.textfilestore.add_note(self.contact, note2)
        with self.assertRaises(AssertionError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1,
                                                self.date2)
        self.assertTrue(self.contact.has_note(self.date1))
        self.assertTrue(self.contact.has_note(self.date2))

    def test_delete_note(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertTrue(self.contact.has_note(self.date1))
        self.core.textfilestore.delete_note(self.contact, self.date1)
        self.assertFalse(self.contact.has_note(self.date1))

    def test_delete_note_date_error(self):
        pass

    def test_delete_note_last_in_dir(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertEqual(len(self.contact.get_notes()), 1)
        self.assertTrue(self.contact.has_note(self.date1))
        self.core.textfilestore.delete_note(self.contact, self.date1)
        self.assertFalse(self.contact.has_note(self.date1))
        self.assertFalse(self.contact.has_notes())

    def test_delete_note_not_existing(self):
        self.assertFalse(self.contact.has_note(self.date1))
        with self.assertRaises(AssertionError):
            self.core.textfilestore.delete_note(self.contact, self.date1)

    def test_edit_note(self):
        self.core.textfilestore.add_note(self.contact, self.note1)
        self.assertTrue(self.contact.has_note(self.date1))
        self.core.textfilestore.edit_note(self.contact, self.date1,
                                          self.note_content2)
        self.assertTrue(self.contact.has_note(self.date1))
        res = self.contact.get_note(self.date1)
        self.assertEqual(res, self.note_content2)

    def test_edit_note_date_error(self):
        pass

    def test_edit_note_not_existing(self):
        self.assertFalse(self.contact.has_note(self.date1))
        with self.assertRaises(AssertionError):
            self.core.textfilestore.edit_note(self.contact, self.date1,
                                              self.note_content2)

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact)

    @classmethod
    def tearDownClass(self):
        pass


class TestKeybindings(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def setUp(self):
        self.core = Core(config, True)
        UI(self.core, config)
        self.core.ui.set_contact_list(self.core.get_all_contacts())

    def test_init(self):
        commands = self.core.keybindings.commands
        self.assertEqual(set(commands.keys()), {
            "global",
            "contact_list",
            "contact_details",
            "contact_entry",
            "attribute_entry",
            "gift_entry",
            "note_entry"
        })
        self.assertSetEqual(set(commands["global"].keys()), {
            "t", "r", "d", "n", "gg", "G", "ctrl r", "I", "ii", "in", "ie", "q"
        })
        self.assertSetEqual(set(commands["contact_list"].keys()), {
            "ig", "/", "zz", "Z"
        })
        self.assertSetEqual(set(commands["contact_details"].keys()), {"ig"})
        self.assertEqual(commands["global"]["I"], "add_contact")
        self.assertEqual(commands["contact_list"]["ig"], "add_google_contact")
        self.assertEqual(commands["contact_details"]["ig"], "add_gift")

    def test_keypress(self):
        command_id, command_key, command_repeat = \
            self.core.keybindings.keypress("t", "global")
        self.assertEqual(command_id, "move_down")

    def test_composed_keypress(self):
        command_id, command_key, command_repeat = \
            self.core.keybindings.keypress("ctrl r", "global")
        self.assertEqual(command_id, "reload")

    def test_multi_keypress(self):
        self.core.keybindings.keypress("g", "global")
        command_id, command_key, command_repeat = \
            self.core.keybindings.keypress("g", "global")
        self.assertEqual(command_id, "jump_to_first")

    def test_command_repeat(self):
        self.core.keybindings.keypress("5", "global")
        command_id, command_key, command_repeat = \
            self.core.keybindings.keypress("t", "global")
        self.assertEqual(command_id, "move_down")
        self.assertEqual(command_repeat, 5)

    def test_widget_keypress(self):
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "t")
        contact_pos = self.core.ui.list_view.get_focus_position()
        self.assertEqual(contact_pos, 2)

    def test_widget_multi_keypress(self):
        self.core.ui.frame.keypress([50, 50], "G")
        contact_pos = self.core.ui.list_view.get_focus_position()
        self.assertEqual(contact_pos, 5)
        self.core.ui.frame.keypress([50, 50], "g")
        self.core.ui.frame.keypress([50, 50], "g")
        contact_pos = self.core.ui.list_view.get_focus_position()
        self.assertEqual(contact_pos, 0)

    def test_widget_command_repeat_detail(self):
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "n")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "d")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "t")
        contact_pos = self.core.ui.list_view.get_focus_position()
        self.assertEqual(contact_pos, 3)

    def test_widget_command_repeat(self):
        self.core.ui.frame.keypress([50, 50], "2")
        self.core.ui.frame.keypress([50, 50], "t")
        contact_pos = self.core.ui.list_view.get_focus_position()
        self.assertEqual(contact_pos, 2)

    def test_widget_command_filter_contact_list(self):
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        mode = self.core.cli.mode
        self.assertEqual(mode, Mode.FILTER)

    def test_widget_command_filter_contact_details_noop(self):
        self.core.ui.frame.keypress([50, 50], "n")
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        mode = self.core.cli.mode
        self.assertEqual(mode, None)
        self.core.ui.frame.keypress([50, 50], "d")
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        mode = self.core.cli.mode
        self.assertEqual(mode, Mode.FILTER)

    @classmethod
    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass


class TestListViewUI(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def setUp(self):
        self.core = Core(config, True)
        UI(self.core, config)
        self.core.ui.set_contact_list(self.core.get_all_contacts())

        self.name1 = "Test Contact A"
        self.name2 = "Test Contact B"
        self.name_first = "A"
        self.name_last = "zzz"
        self.contact1 = Contact(self.name1, self.core)
        self.contact2 = Contact(self.name2, self.core)
        self.contact_first = Contact(self.name_first, self.core)
        self.contact_last = Contact(self.name_last, self.core)
        self.pos = 0

    # test initialization entries objects

    def test_init_attribute_entry(self):
        attribute = Attribute("key", "value")
        entry = AttributeEntry(self.contact1, attribute, self.pos, self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_gift_entry(self):
        gift = Gift("name")
        entry = GiftEntry(self.contact1, gift, self.pos, self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_note_entry(self):
        note = Note("20200101", "Text")
        entry = NoteEntry(self.contact1, note, self.pos, self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_contact_entry(self):
        entry = ContactEntry(self.contact1, self.core, self.pos)
        self.assertIsInstance(entry.label, str)

    # test focusing of contacts after CRUD operations

    def test_focus_add_first(self):
        self.core.cli.handle(['add-contact', self.name_first])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_first)
        pos = self.core.ui.list_view.get_contact_position(focused_contact)
        self.assertEqual(pos, 0)

    def test_focus_add_some(self):
        self.core.cli.handle(['add-contact', self.name1])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name1)

    def test_focus_add_two(self):
        # contact 1
        self.core.cli.handle(['add-contact', self.name1])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name1)
        # contact 2
        self.core.cli.handle(['add-contact', self.name2])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_add_last(self):
        self.core.cli.handle(['add-contact', self.name_last])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_last)

    def test_focus_rename_first_to_some(self):
        self.core.add_contact(self.contact_first)
        self.core.ui.update_view(True, False, None, self.contact_first)
        self.core.cli.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_some_to_some(self):
        self.core.add_contact(self.contact1)
        self.core.ui.update_view(True, False, None, self.contact1)
        self.core.cli.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_last_to_some(self):
        self.core.add_contact(self.contact_last)
        self.core.ui.update_view(True, False, None, self.contact_last)
        self.core.cli.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_some_to_first(self):
        self.core.add_contact(self.contact1)
        self.core.ui.update_view(True, False, None, self.contact1)
        self.core.cli.handle(['rename-contact', self.name_first])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_first)
        new_pos = self.core.ui.list_view.get_contact_position(focused_contact)
        self.assertEqual(new_pos, 0)

    def test_focus_rename_some_to_last(self):
        self.core.add_contact(self.contact1)
        self.core.ui.update_view(True, False, None, self.contact1)
        self.core.cli.handle(['rename-contact', self.name_last])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_last)

    def test_focus_delete_first(self):
        self.core.add_contact(self.contact_first)
        self.core.cli.handle(['delete-contact', self.name_first])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(focused_contact)
        self.assertEqual(new_pos, 0)
        self.assertNotEqual(focused_contact.name, self.name_last)

    def test_focus_delete_some(self):
        self.core.add_contact(self.contact_last)
        self.core.add_contact(self.contact1)
        self.core.add_contact(self.contact2)
        self.core.ui.update_view(True, False, None, self.contact1)
        pos = self.core.ui.list_view.get_contact_position(self.contact1)
        self.core.cli.handle(['delete-contact', self.name1])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(focused_contact)
        self.assertEqual(new_pos, pos)
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_delete_last(self):
        self.core.add_contact(self.contact_last)
        self.core.ui.update_view(True, False, None, self.contact_last)
        pos = self.core.ui.list_view.get_contact_position(self.contact_last)
        self.core.cli.handle(['delete-contact', self.name_last])
        focused_contact = self.core.ui.list_view.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(focused_contact)
        self.assertEqual(new_pos, pos - 1)
        self.assertNotEqual(focused_contact.name, self.name_last)

    def test_focus_delete_when_next_no_attributes(self):
        pass
        # TODO
        # previous = Contact("zzy")
        # self.core.
        # self.core.add_contact(self.contact_last)

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact1)
        self.core.delete_contact(self.contact2)
        self.core.delete_contact(self.contact_first)
        self.core.delete_contact(self.contact_last)

    @classmethod
    def tearDownClass(self):
        pass


class TestTUIDetailFocusFirstContact(unittest.TestCase):
    """
    Test focusing of details after CRUD operations
    """

    @classmethod
    def setUp(self):
        self.core = Core(config, True)
        self.name_first = "A"
        self.contact_first = Contact(self.name_first, self.core)
        self.core.add_contact(self.contact_first)
        self.core.ui.refresh_contact_list(Action.CONTACT_ADDED_OR_EDITED,
                                          self.contact_first)

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact_first)

    def test_setup(self):
        self.ct_pos = self.core.ui.list_view.get_contact_position(
            self.contact_first)
        self.assertEqual(self.ct_pos, 0)

    def test_focus_add_first_detail_to_first_contact(self):
        pass

    def test_focus_add_some_detail_to_first_contact(self):
        pass

    def test_focus_add_two_detail_to_first_contact(self):
        pass

    def test_focus_add_last_detail_to_first_contact(self):
        pass

    def test_focus_edit_first_to_some_detail_of_first_contact(self):
        pass

    def test_focus_edit_some_to_some_detail_of_first_contact(self):
        pass

    def test_focus_edit_last_to_some_detail_of_first_contact(self):
        pass

    def test_focus_edit_some_to_first_detail_of_first_contact(self):
        pass

    def test_focus_edit_some_to_last_detail_of_first_contact(self):
        pass

    def test_focus_delete_first_detail_from_first_contact(self):
        pass

    def test_focus_delete_some_detail_from_first_contact(self):
        pass

    def test_focus_delete_last_detail_from_first_contact(self):
        pass


class TestTUIDetailFocusSomeContact(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.core = Core(config, True)
        self.name1 = "Test Contact A"
        self.contact1 = Contact(self.name1, self.core)
        self.core.add_contact(self.contact1)
        self.core.ui.refresh_contact_list(Action.CONTACT_ADDED_OR_EDITED,
                                          self.contact1)

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact1)

    def test_setup(self):
        self.ct_pos = self.core.ui.list_view.get_contact_position(
            self.contact1)
        self.assertNotEqual(self.ct_pos, 0)  # not first
        contact_list_length = len(self.core.ui.list_view.body)
        self.assertNotEqual(self.ct_pos, contact_list_length)  # not last

    def test_focus_add_first_detail_to_some_contact(self):
        pass

    def test_focus_add_some_detail_to_some_contact(self):
        pass

    def test_focus_add_two_detail_to_some_contact(self):
        pass

    def test_focus_add_last_detail_to_some_contact(self):
        pass

    def test_focus_edit_first_to_some_detail_of_some_contact(self):
        pass

    def test_focus_edit_some_to_some_detail_of_some_contact(self):
        pass

    def test_focus_edit_last_to_some_detail_of_some_contact(self):
        pass

    def test_focus_edit_some_to_first_detail_of_some_contact(self):
        pass

    def test_focus_edit_some_to_last_detail_of_some_contact(self):
        pass

    def test_focus_delete_first_detail_from_some_contact(self):
        pass

    def test_focus_delete_some_detail_from_some_contact(self):
        pass

    def test_focus_delete_last_detail_from_some_contact(self):
        pass


class TestTUIDetailFocusLastContact(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.core = Core(config, True)
        self.name_last = "zzz"
        self.contact_last = Contact(self.name_last, self.core)
        self.core.add_contact(self.contact_last)
        self.core.ui.refresh_contact_list(Action.CONTACT_ADDED_OR_EDITED,
                                          self.contact_last)

    @classmethod
    def tearDown(self):
        self.core.delete_contact(self.contact_last)

    def test_setup(self):
        self.ct_pos = self.core.ui.list_view.get_contact_position(
            self.contact_last)
        contact_list_length = len(self.core.ui.list_view.body)
        self.assertEqual(self.ct_pos, contact_list_length - 1)

    def test_focus_add_first_detail_to_last_contact(self):
        pass

    def test_focus_add_some_detail_to_last_contact(self):
        pass

    def test_focus_add_two_detail_to_last_contact(self):
        pass

    def test_focus_add_last_detail_to_last_contact(self):
        pass

    def test_focus_edit_first_to_some_detail_of_last_contact(self):
        pass

    def test_focus_edit_some_to_some_detail_of_last_contact(self):
        pass

    def test_focus_edit_last_to_some_detail_of_last_contact(self):
        pass

    def test_focus_edit_some_to_first_detail_of_last_contact(self):
        pass

    def test_focus_edit_some_to_last_detail_of_last_contact(self):
        pass

    def test_focus_delete_first_detail_from_last_contact(self):
        pass

    def test_focus_delete_some_detail_from_last_contact(self):
        pass

    def test_focus_delete_last_detail_from_last_contact(self):
        pass


if __name__ == '__main__':
    unittest.main()
