from datetime import datetime


class Note:

    def __init__(self, note_id: object, content: object) -> object:
        Note.validate_name(note_id)

        self.note_id = note_id
        self.content = content

    def __eq__(self, other):
        return self.note_id == other.note_id

    @classmethod
    def validate_name(cls, name):
        try:
            datetime.strptime(name, '%Y%m%d')
        except ValueError:
            raise ValueError(
                f'Error: Invalid note name: "{name}". Note names match the pattern YYYYMMDD')
