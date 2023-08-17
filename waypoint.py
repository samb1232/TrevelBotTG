class Waypoint:
    text: str = None
    picture_source: str = None
    audio_source: str = None
    next_point: str = None

    def __init__(self, text: str = None, picture_source: str = None, audio_source: str = None, next_point: str = None) -> None:
        self.text = text
        self.picture_source = picture_source
        self.audio_source = audio_source
        self.next_point = next_point
