class Track:
    def __init__(self, name, artists) -> None:
        self.name = name
        self.artists = artists
        self.image_url = ""
        self.duration_in_ms = 0
        self.progress_in_ms = 0
        self.is_playing = False
        self.is_shuffle = False
        self.repeat_state = "off"

    def artists_in_str(self):
        return ', '.join(self.artists)
    
    def duration_in_min_sec(self):
        sec = self.duration_in_ms / 1000
        min = int(sec // 60)
        sec = int(sec % 60)
        return f"{min}:{sec:02d}"
    
    def progress_in_min_sec(self):
        sec = self.progress_in_ms / 1000
        min = int(sec // 60)
        sec = int(sec % 60)
        return f"{min}:{sec:02d}"
