from ctui.model.note import Note


class EncryptedNote(Note):

    def __init__(self, note_id, content=None):
        super().__init__(note_id, content)
        super().validate_name(note_id)

        self.note_id = note_id
        self.content = content
