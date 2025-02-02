class GoogleAttribute:

    def __init__(self, key, value, google_key):
        self.key = key
        self.value = value
        self.google_key = google_key

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value
