import os
from subprocess import call


class Editor:
    def __init__(self, core, editor_name):
        self.core = core
        self.editor = os.environ.get('EDITOR', editor_name)

    def add(self, filepath):
        temp_filepath = filepath + '.tmp'

        try:
            with open(temp_filepath, 'w') as tf:
                call([self.editor, tf.name])
                self.core.ui.main_loop.screen.clear()  # redraw screen

            with open(temp_filepath, 'r') as tf:
                content = tf.read()

            os.remove(temp_filepath)

        except OSError:
            raise OSError  # TODO

        return content

    def edit(self, filepath):
        temp_filepath = filepath + '.tmp'

        try:
            with open(filepath) as f:
                old_content = f.read()

            with open(temp_filepath, 'w') as tf:
                tf.write(old_content)
                tf.flush()
                call([self.editor, tf.name])
                self.core.ui.main_loop.screen.clear()  # redraw screen

            with open(temp_filepath, 'r') as tf:
                content = tf.read()

            os.remove(temp_filepath)

        except OSError:
            raise OSError  # TODO

        return content
