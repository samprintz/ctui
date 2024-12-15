import unittest

import ctui.util as util
from ctui.component.contact_entry import ContactEntry
from ctui.component.contact_list import ContactList
from ctui.component.detail_entry import AttributeEntry, GiftEntry, NoteEntry
from ctui.core import *
from ctui.model.attribute import Attribute
from ctui.model.gift import Gift
from ctui.model.note import Note
from ctui.ui import UI

CONFIG_FILE = 'files/config.ini'
config = util.load_config(CONFIG_FILE)


class TestCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core(config, True)
        cls.name1 = "Test Contact A"
        cls.name2 = "Test Contact B"
        cls.contact1 = Contact(cls.name1)
        cls.contact2 = Contact(cls.name2)

    @classmethod
    def setUp(cls):
        pass

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
        self.core.rdfstore.add_attribute(self.contact1, attr)
        self.assertTrue(self.core.rdfstore.has_attribute(self.contact1, attr))
        res = self.core.delete_contact(self.contact1)
        self.assertFalse(self.core.contains_contact(self.contact1))
        self.assertFalse(self.core.rdfstore.contains_attribute(attr))

    @classmethod
    def tearDown(cls):
        cls.core.delete_contact(cls.contact1)
        cls.core.delete_contact(cls.contact2)

    @classmethod
    def tearDownClass(cls):
        pass


class TestContactHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core(config, True)
        cls.name = "Max Mustermann"
        cls.contact = Contact(cls.name)

    @classmethod
    def setUp(cls):
        pass

    def test_load_contact_names(self):
        contact_names = self.core.contact_handler.load_contact_names()
        self.assertIsNotNone(contact_names)
        self.assertIsInstance(contact_names, list)


class TestObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core(config, True)
        cls.name = "Test Contact"
        cls.contact = Contact(cls.name)
        cls.attr_key1 = "key1"
        cls.attr_key2 = "key2"
        cls.attr_value1 = "Attribute 1"
        cls.attr_value2 = "Attribute 2"
        cls.attr1 = Attribute(cls.attr_key1, cls.attr_value1)
        cls.attr2 = Attribute(cls.attr_key2, cls.attr_value2)
        cls.gift_name1 = "Gift 1"
        cls.gift_name2 = "Gift 2"
        cls.gift_content_new = "desc: new description"
        cls.gift_content_invalid = "invalid content"
        cls.gift1 = Gift(cls.gift_name1, "")
        cls.gift2 = Gift(cls.gift_name2, "")
        cls.note_id1 = "19990101"
        cls.note_id2 = "19991215"
        cls.note_id_invalid = "1248"
        cls.note_content1 = "Text 1"
        cls.note_content2 = "Text 2"
        cls.note1 = Note(cls.note_id1, cls.note_content1)

    @classmethod
    def setUp(cls):
        cls.core.add_contact(cls.contact)

    # attributes

    def test_add_attr(self):
        res = self.core.rdfstore.add_attribute(self.contact, self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))

    def test_add_attr_already_existing(self):
        self.core.rdfstore.add_attribute(self.contact, self.attr1)
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))
        res = self.core.rdfstore.add_attribute(self.contact, self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))

    def test_edit_attr(self):
        self.core.rdfstore.add_attribute(self.contact, self.attr1)
        res = self.core.rdfstore.edit_attribute(self.contact, self.attr1,
                                                self.attr2)
        self.assertIsNotNone(res)
        self.assertFalse(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr2))

    def test_edit_attr_unchanged(self):
        self.core.rdfstore.add_attribute(self.contact, self.attr1)
        res = self.core.rdfstore.edit_attribute(self.contact, self.attr1,
                                                self.attr1)
        self.assertIsNotNone(res)
        self.assertTrue(res.startswith("Warning"))
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))

    def test_edit_attr_not_existing(self):
        self.assertFalse(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))

        with self.assertRaises(ValueError):
            self.core.rdfstore.edit_attribute(self.contact, self.attr1,
                                              self.attr2)

    def test_delete_attr(self):
        self.core.rdfstore.add_attribute(self.contact, self.attr1)
        self.assertTrue(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))
        res = self.core.rdfstore.delete_attribute(self.contact, self.attr1)
        self.assertIsNotNone(res)
        self.assertFalse(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))

    def test_delete_attr_not_existing(self):
        self.assertFalse(
            self.core.rdfstore.has_attribute(self.contact, self.attr1))
        with self.assertRaises(ValueError):
            self.core.rdfstore.delete_attribute(self.contact, self.attr1)

    # gifts

    def test_add_gift(self):
        res = self.core.textfilestore.add_gift(self.contact.get_id(),
                                               self.gift1)
        self.assertIsNotNone(res)
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))

    def test_add_gift_already_existing(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))

        with self.assertRaises(ValueError):
            self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)

    def test_rename_gift(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        res = self.core.textfilestore.rename_gift(self.contact.get_id(),
                                                  self.gift1.get_id(),
                                                  self.gift_name2)
        self.assertIsNotNone(res)
        self.assertFalse(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift2.get_id()))

    def test_edit_gift(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)

        new_gift = Gift.from_dump(self.gift1.get_id(), self.gift_content_new)

        self.core.textfilestore.edit_gift(self.contact.get_id(),
                                          self.gift1.get_id(), new_gift)

        res = self.core.textfilestore.get_gift(self.contact.get_id(),
                                               self.gift1.get_id())

        self.assertEqual(res.to_dump(), self.gift_content_new)

    def test_edit_gift_invalid_content(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)

        with self.assertRaises(ValueError):
            Gift.from_dump(self.gift1.get_id(), self.gift_content_invalid)

    def test_mark_gifted(self):
        self.gift1.gifted = False
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.core.textfilestore.mark_gifted(self.contact.get_id(),
                                            self.gift1.get_id())
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        res = self.core.textfilestore.get_gift(self.contact.get_id(),
                                               self.gift1.get_id())
        self.assertTrue(res.gifted)

    def test_unmark_gifted(self):
        self.gift1.gifted = True
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.core.textfilestore.unmark_gifted(self.contact.get_id(),
                                              self.gift1.get_id())
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        res = self.core.textfilestore.get_gift(self.contact.get_id(),
                                               self.gift1.get_id())
        self.assertFalse(res.gifted)

    def test_mark_permanent(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.core.textfilestore.mark_permanent(self.contact.get_id(),
                                               self.gift1.get_id())
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        res = self.core.textfilestore.get_gift(self.contact.get_id(),
                                               self.gift1.get_id())
        self.assertTrue(res.permanent)

    def test_unmark_permanent(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.core.textfilestore.unmark_permanent(self.contact.get_id(),
                                                 self.gift1.get_id())
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        res = self.core.textfilestore.get_gift(self.contact.get_id(),
                                               self.gift1.get_id())
        self.assertFalse(res.permanent)

    def test_edit_gift_not_existing(self):
        self.assertFalse(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))

        with self.assertRaises(ValueError):
            self.core.textfilestore.edit_gift(
                self.contact.get_id(),
                self.gift1.get_id(),
                self.gift2
            )

    def test_delete_gift(self):
        self.core.textfilestore.add_gift(self.contact.get_id(), self.gift1)
        self.assertTrue(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))
        res = self.core.textfilestore.delete_gift(self.contact.get_id(),
                                                  self.gift1.get_id())
        self.assertIsNotNone(res)
        self.assertFalse(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))

    def test_delete_gift_not_existing(self):
        self.assertFalse(
            self.core.textfilestore.has_gift(self.contact.get_id(),
                                             self.gift1.get_id()))

        with self.assertRaises(ValueError):
            self.core.textfilestore.delete_gift(
                self.contact.get_id(),
                self.gift1.get_id()
            )

    # notes

    def test_add_note_new_dir(self):
        self.assertFalse(self.core.textfilestore.contains_contact(self.contact))
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id1))

    def test_add_note_existing_dir(self):
        self.core.textfilestore.add_contact(self.contact)
        self.assertTrue(self.core.textfilestore.contains_contact(self.contact))
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id1))

    def test_add_note_date_error(self):
        pass

    def test_add_note_already_existing(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id1))

        with self.assertRaises(ValueError):
            self.core.textfilestore.add_note(self.contact.get_id(), self.note1)

    def test_rename_note(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        self.core.textfilestore.rename_note(self.contact.get_id(),
                                            self.note1.note_id,
                                            self.note_id2)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id2))
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))

    def test_rename_note_date_error(self):
        pass

    def test_rename_note_unchanged(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)

        with self.assertRaises(ValueError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1.note_id,
                                                self.note_id1)

    def test_rename_note_not_existing(self):
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))

        with self.assertRaises(ValueError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1.note_id,
                                                self.note_id2)

    def test_rename_note_already_existing(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        note2 = Note(self.note_id2, self.note_content2)
        self.core.textfilestore.add_note(self.contact.get_id(), note2)

        with self.assertRaises(ValueError):
            self.core.textfilestore.rename_note(self.contact.get_id(),
                                                self.note1.note_id,
                                                note2.note_id)

    def test_delete_note(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id1))
        self.core.textfilestore.delete_note(self.contact.get_id(),
                                            self.note_id1)
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))

    def test_delete_note_date_error(self):
        pass

    def test_delete_note_last_in_dir(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)
        res = self.core.textfilestore.get_notes(self.contact.get_id())
        self.assertEqual(len(res), 1)
        self.assertTrue(self.core.textfilestore.has_note(self.contact.get_id(),
                                                         self.note_id1))
        self.core.textfilestore.delete_note(self.contact.get_id(),
                                            self.note_id1)
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))
        self.assertFalse(
            self.core.textfilestore.has_notes(self.contact.get_id()))

    def test_delete_note_not_existing(self):
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))
        with self.assertRaises(ValueError):
            self.core.textfilestore.delete_note(self.contact.get_id(),
                                                self.note_id1)

    def test_edit_note(self):
        self.core.textfilestore.add_note(self.contact.get_id(), self.note1)

        new_note = Note.from_dump(self.note_id1, self.note_content2)

        self.core.textfilestore.edit_note(self.contact.get_id(), self.note_id1,
                                          new_note)

        res = self.core.textfilestore.get_note(self.contact.get_id(),
                                               self.note_id1)

        self.assertEqual(res.content, self.note_content2)

    def test_edit_note_date_error(self):
        pass

    def test_edit_note_not_existing(self):
        self.assertFalse(self.core.textfilestore.has_note(self.contact.get_id(),
                                                          self.note_id1))

        new_note = Note.from_dump(self.note_id1, self.note_content2)

        with self.assertRaises(ValueError):
            self.core.textfilestore.edit_note(self.contact.get_id(),
                                              self.note_id1,
                                              new_note)

    @classmethod
    def tearDown(cls):
        cls.core.delete_contact(cls.contact)

    @classmethod
    def tearDownClass(cls):
        pass


class TestKeybindings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def setUp(cls):
        cls.core = Core(config, True)
        UI(cls.core, config)

    def test_init(self):
        commands = self.core.keybindings.commands
        self.assertEqual(set(commands.keys()), {
            "global",
            "contact_list",
            'contact_note_details',
            "contact_entry",
            "attribute_entry",
            "gift_entry",
            "note_entry"
        })
        self.assertSetEqual(set(commands["global"].keys()), {
            "t", "r", "d", "n", "gg", "G", "N", "D", "ctrl r", "I", "ii", "q"
        })
        self.assertSetEqual(set(commands["contact_list"].keys()), {
            "ig", "/", "zz", "Z"
        })
        self.assertSetEqual(set(commands["contact_note_details"].keys()),
                            {"ie"})
        self.assertEqual(commands["global"]["I"], "add_contact")
        self.assertEqual(commands["contact_list"]["ig"], "add_google_contact")
        self.assertEqual(commands["contact_note_details"]["ie"],
                         "add_encrypted_note")

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
        contact_pos = self.core.ui.get_focused_contact_pos()
        self.assertEqual(contact_pos, 2)

    def test_widget_multi_keypress(self):
        self.core.ui.frame.keypress([50, 50], "G")
        contact_pos = self.core.ui.get_focused_contact_pos()
        self.assertEqual(contact_pos, 3)
        self.core.ui.frame.keypress([50, 50], "g")
        self.core.ui.frame.keypress([50, 50], "g")
        contact_pos = self.core.ui.get_focused_contact_pos()
        self.assertEqual(contact_pos, 0)

    def test_widget_command_repeat_detail(self):
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "n")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "d")
        self.core.ui.frame.keypress([50, 50], "t")
        self.core.ui.frame.keypress([50, 50], "t")
        contact_pos = self.core.ui.get_focused_contact_pos()
        self.assertEqual(contact_pos, 3)

    def test_widget_command_repeat(self):
        self.core.ui.frame.keypress([50, 50], "2")
        self.core.ui.frame.keypress([50, 50], "t")
        contact_pos = self.core.ui.get_focused_contact_pos()
        self.assertEqual(contact_pos, 2)

    def test_widget_command_filter_contact_list(self):
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        self.assertTrue(self.core.ui.console.filter_mode)

    def test_widget_command_filter_contact_details_noop(self):
        self.core.ui.frame.keypress([50, 50], "n")
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        self.assertFalse(self.core.ui.console.filter_mode)
        self.core.ui.frame.keypress([50, 50], "d")
        self.core.ui.frame.keypress([50, 50], "z")
        self.core.ui.frame.keypress([50, 50], "z")
        self.assertTrue(self.core.ui.console.filter_mode)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class TestListViewUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def setUp(cls):
        cls.core = Core(config, True)
        UI(cls.core, config)

        cls.name1 = "Test Contact A"
        cls.name2 = "Test Contact B"
        cls.name_first = "A"
        cls.name_last = "zzz"
        cls.contact1 = Contact(cls.name1)
        cls.contact2 = Contact(cls.name2)
        cls.contact_first = Contact(cls.name_first)
        cls.contact_last = Contact(cls.name_last)
        cls.pos = 0

    # test initialization entries objects

    def test_init_attribute_entry(self):
        attribute = Attribute("key", "value")
        entry = AttributeEntry(self.contact1.get_id(), attribute, self.pos,
                               self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_gift_entry(self):
        gift = Gift("name")
        entry = GiftEntry(self.contact1.get_id(), gift, self.pos, self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_note_entry(self):
        note = Note("20200101", "Text")
        entry = NoteEntry(self.contact1.get_id(), note, self.pos, self.core)
        self.assertIsInstance(entry.label, str)

    def test_init_contact_entry(self):
        entry = ContactEntry(self.contact1, self.core, self.pos)
        self.assertIsInstance(entry.label, str)

    # test focusing of contacts after CRUD operations

    def test_focus_add_first(self):
        self.core.ui.console.handle(['add-contact', self.name_first])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_first)
        pos = self.core.ui.list_view.get_contact_position(
            focused_contact.get_id())
        self.assertEqual(pos, 0)

    def test_focus_add_some(self):
        self.core.ui.console.handle(['add-contact', self.name1])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name1)

    def test_focus_add_two(self):
        # contact 1
        self.core.ui.console.handle(['add-contact', self.name1])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name1)
        # contact 2
        self.core.ui.console.handle(['add-contact', self.name2])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_add_last(self):
        self.core.ui.console.handle(['add-contact', self.name_last])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_last)

    def test_focus_rename_first_to_some(self):
        self.core.add_contact(self.contact_first)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact_first.get_id())

        self.core.ui.console.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_some_to_some(self):
        self.core.add_contact(self.contact1)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact1.get_id())

        self.core.ui.console.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_last_to_some(self):
        self.core.add_contact(self.contact_last)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact_last.get_id())

        self.core.ui.console.handle(['rename-contact', self.name2])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_rename_some_to_first(self):
        self.core.add_contact(self.contact1)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact1.get_id())

        self.core.ui.console.handle(['rename-contact', self.name_first])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_first)
        new_pos = self.core.ui.list_view.get_contact_position(
            focused_contact.get_id())
        self.assertEqual(new_pos, 0)

    def test_focus_rename_some_to_last(self):
        self.core.add_contact(self.contact1)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact1.get_id())

        self.core.ui.console.handle(['rename-contact', self.name_last])
        focused_contact = self.core.ui.get_focused_contact()
        self.assertEqual(focused_contact.name, self.name_last)

    def test_focus_delete_first(self):
        self.core.add_contact(self.contact_first)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact_first.get_id())

        self.core.ui.console.handle(['delete-contact', self.name_first])
        focused_contact = self.core.ui.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(
            focused_contact.get_id())
        self.assertEqual(new_pos, 0)
        self.assertNotEqual(focused_contact.name, self.name_last)

    def test_focus_delete_some(self):
        self.core.add_contact(self.contact_last)
        self.core.add_contact(self.contact1)
        self.core.add_contact(self.contact2)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact1.get_id())
        pos = self.core.ui.list_view.get_contact_position(
            self.contact1.get_id())

        self.core.ui.console.handle(['delete-contact', self.name1])
        focused_contact = self.core.ui.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(
            focused_contact.get_id())
        self.assertEqual(new_pos, pos)
        self.assertEqual(focused_contact.name, self.name2)

    def test_focus_delete_last(self):
        self.core.add_contact(self.contact_last)
        self.core.update_contact_list()
        self.core.ui.set_focused_contact(self.contact_last.get_id())
        pos = self.core.ui.list_view.get_contact_position(
            self.contact_last.get_id())

        self.core.ui.console.handle(['delete-contact', self.name_last])
        focused_contact = self.core.ui.get_focused_contact()
        new_pos = self.core.ui.list_view.get_contact_position(
            focused_contact.get_id())
        self.assertEqual(new_pos, pos - 1)
        self.assertNotEqual(focused_contact.name, self.name_last)

    def test_focus_delete_when_next_no_attributes(self):
        pass
        # TODO
        # previous = Contact("zzy")
        # self.core.
        # self.core.add_contact(self.contact_last)

    @classmethod
    def tearDown(cls):
        cls.core.delete_contact(cls.contact1)
        cls.core.delete_contact(cls.contact2)
        cls.core.delete_contact(cls.contact_first)
        cls.core.delete_contact(cls.contact_last)

    @classmethod
    def tearDownClass(cls):
        pass


class TestUIDetailView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def setUp(cls):
        cls.core = Core(config, True)
        UI(cls.core, config)

        cls.name_first = "A"
        cls.attr_key_first = "aaa-key"
        cls.attr_key1 = "key1"
        cls.attr_key2 = "key2"
        cls.attr_key_last = "zzz-key"
        cls.attr_value1 = "Attribute 1"
        cls.attr_value2 = "Attribute 2"

        cls.contact_first = Contact(cls.name_first)
        cls.core.add_contact(cls.contact_first)
        cls.core.update_contact_list()

    @classmethod
    def tearDown(cls):
        cls.core.delete_contact(cls.contact_first)

    def test_setup(self):
        self.ct_pos = self.core.ui.list_view.get_contact_position(
            self.contact_first.get_id())
        self.assertEqual(self.ct_pos, 0)

    def test_focus_add_first_detail_to_first_contact(self):
        self.core.ui.console.handle(
            ['add-attribute', self.attr_key1, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key1)
        self.assertEqual(focused_detail_pos, 0)

    def test_focus_add_some_detail_to_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_last = Attribute(self.attr_key_last, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_last)

        self.core.ui.console.handle(
            ['add-attribute', self.attr_key2, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key2)
        self.assertEqual(focused_detail_pos, 2)

    def test_focus_add_two_detail_to_first_contact(self):
        self.core.ui.console.handle(
            ['add-attribute', self.attr_key1, self.attr_value1])
        self.core.ui.console.handle(
            ['add-attribute', self.attr_key2, self.attr_value2])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key2)
        self.assertEqual(focused_detail_pos, 1)

    def test_focus_add_last_detail_to_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)

        self.core.ui.console.handle(
            ['add-attribute', self.attr_key_last, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key_last)
        self.assertEqual(focused_detail_pos, 2)

    def test_focus_edit_first_to_some_detail_of_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_first)

        self.core.ui.console.handle(
            ['edit-attribute', self.attr_key2, self.attr_value2])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key2)
        self.assertEqual(focused_detail_pos, 1)

    def test_focus_edit_some_to_some_detail_of_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_last = Attribute(self.attr_key_last, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_last)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_1)

        self.core.ui.console.handle(
            ['edit-attribute', self.attr_key2, self.attr_value2])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key2)
        self.assertEqual(focused_detail_pos, 1)

    def test_focus_edit_last_to_some_detail_of_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_2 = Attribute(self.attr_key1, self.attr_value2)
        attr_last = Attribute(self.attr_key_last, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_2)
        self.core.rdfstore.add_attribute(self.contact_first, attr_last)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_last)

        self.core.ui.console.handle(
            ['edit-attribute', self.attr_key1, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key1)
        self.assertEqual(focused_detail_pos, 1)

    def test_focus_edit_some_to_first_detail_of_first_contact(self):
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_2 = Attribute(self.attr_key2, self.attr_value2)
        attr_last = Attribute(self.attr_key_last, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_2)
        self.core.rdfstore.add_attribute(self.contact_first, attr_last)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_2)

        self.core.ui.console.handle(
            ['edit-attribute', self.attr_key_first, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key_first)
        self.assertEqual(focused_detail_pos, 0)

    def test_focus_edit_some_to_last_detail_of_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_2 = Attribute(self.attr_key2, self.attr_value2)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_2)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_1)

        self.core.ui.console.handle(
            ['edit-attribute', self.attr_key_last, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key_last)
        self.assertEqual(focused_detail_pos, 2)

    def test_focus_delete_first_detail_from_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_first)

        self.core.ui.console.handle(
            ['delete-attribute', self.attr_key_first, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key1)
        self.assertEqual(focused_detail_pos, 0)

    def test_focus_delete_some_detail_from_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_2 = Attribute(self.attr_key2, self.attr_value2)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_2)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_1)

        self.core.ui.console.handle(
            ['delete-attribute', self.attr_key1, self.attr_value1])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key2)
        self.assertEqual(focused_detail_pos, 1)

    def test_focus_delete_last_detail_from_first_contact(self):
        attr_first = Attribute(self.attr_key_first, self.attr_value1)
        attr_1 = Attribute(self.attr_key1, self.attr_value1)
        attr_last = Attribute(self.attr_key_last, self.attr_value2)
        self.core.rdfstore.add_attribute(self.contact_first, attr_first)
        self.core.rdfstore.add_attribute(self.contact_first, attr_1)
        self.core.rdfstore.add_attribute(self.contact_first, attr_last)

        self.core.update_contact_details(self.contact_first.get_id())
        self.core.ui.set_focused_detail(attr_last)

        self.core.ui.console.handle(
            ['delete-attribute', self.attr_key_last, self.attr_value2])

        focused_detail = self.core.ui.get_focused_detail()
        focused_detail_pos = self.core.ui.get_focused_detail_pos()
        self.assertEqual(focused_detail.key, self.attr_key1)
        self.assertEqual(focused_detail_pos, 1)


class TestFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def setUp(cls):
        cls.core = Core(config, True)
        UI(cls.core, config)

    def test_filter(self):
        pass

    def test_set_contact_filter(self):
        self.core.set_contact_filter()
        self.core.update_contact_list("Max")
        self.assertTrue(self.core.ui.console.filter_mode)
        self.assertEqual(self.core.ui.list_view.get_count(), 1)

    def test_set_contact_filter_not_existing(self):
        self.core.set_contact_filter()
        self.core.update_contact_list("Mike")
        self.assertEqual(self.core.ui.list_view.get_count(), 1)
        entry_label = self.core.ui.list_view.focus.label
        self.assertEqual(entry_label, ContactList.no_result_msg)
        detail_view_count = self.core.ui.detail_view.get_count()
        self.assertEqual(detail_view_count, 0)

    def test_reset_contact_filter(self):
        self.core.set_contact_filter()
        self.core.update_contact_list("Max")
        self.assertEqual(self.core.ui.list_view.get_count(), 1)
        self.core.clear_contact_filter()
        self.assertEqual(self.core.ui.list_view.get_count(), 4)
        self.assertEqual(self.core.ui.get_focused_contact().get_id(),
                         "Max_Mustermann")

    def test_reset_contact_filter_not_existing(self):
        self.core.set_contact_filter()
        self.core.update_contact_list("Tom")
        self.assertEqual(self.core.ui.list_view.get_count(), 1)
        self.core.clear_contact_filter()


if __name__ == '__main__':
    unittest.main()
