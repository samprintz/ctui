import urwid


class CListEntry(urwid.Button):
    def __init__(self, label, pos, core):
        super(CListEntry, self).__init__(label)
        self.core = core
        self.pos = pos
        self.set_label(label)

    def set_label(self, label):
        super(CListEntry, self).set_label(label)
        cursor_pos = len(label) + 1
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            label, cursor_pos), None, 'selected')
