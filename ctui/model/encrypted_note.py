from datetime import datetime

from ctui.model.note import Note


class EncryptedNote(Note):

    def __init__(self, note_id, content=None, encrypted=True):
        # TODO refactor like Note
        if isinstance(note_id, str):
            try:
                note_id = datetime.strptime(note_id, '%Y%m%d')
            except ValueError:
                raise ValueError(
                    f'Invalid note name: "{note_id}". Note names match the pattern YYYYMMMDD')
        self.note_id = note_id
        self.content = content

    def __eq__(self, other):
        return self.note_id == other.note_id
