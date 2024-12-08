from datetime import datetime


class Note:

    def __init__(self, note_id, content):
        Note.validate_name(note_id)

        self.note_id = note_id
        self.content = content

    def __eq__(self, other):
        return self.note_id == other.note_id

    def __str__(self):
        return f'Note({self.note_id})'

    def to_dump(self):
        return self.content

    @classmethod
    def from_dump(cls, note_id, dump):
        return Note(note_id, dump)

    @classmethod
    def validate_name(cls, name: str) -> None:
        try:
            datetime.strptime(name, '%Y%m%d')
        except ValueError:
            raise ValueError(
                f'Error: Invalid note name: "{name}". Note names must match the pattern YYYYMMDD')

    @classmethod
    def name_to_id(cls, name):
        return name

    @classmethod
    def id_to_name(cls, note_id):
        return note_id

    @classmethod
    def id_to_filename(cls, note_id):
        return f'{note_id}.yaml'
