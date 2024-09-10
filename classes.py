class Track:
    def __init__(self, name, artists) -> None:
        self.name = name
        self.artists = artists
        self.image_url = ""
        self.duration_in_ms = 0
        self.progress_in_ms = 0
        self.is_playing = False

    def artists_in_str(self):
        return ', '.join(self.artists)
