import urwid


class CFrameColumns(urwid.Columns):
    def __init__(self, list_view, detail_view, core, config):
        self.core = core

        # TODO where does this belong?
        self.focus_map = {'options': 'focus options'}

        self.nav_width = int(config['display']['nav_width'])

        widget_list = [
            (
                'fixed',
                self.nav_width,
                list_view
            ),
            (
                'weight',
                1,
                detail_view
            ),
        ]

        super(CFrameColumns, self).__init__(widget_list, dividechars=1)
